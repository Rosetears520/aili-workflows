from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / '.agents/skills/pptx-generator/scripts'
sys.path.insert(0, str(SCRIPTS))
import officecli_adapter as adapter
import render_with_officecli as render


def write_deck(path: Path, count: int, cx: int = 12192000, cy: int = 6858000) -> None:
    """Geometry fixture only, not a renderable or validated package."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ids = ''.join(f'<p:sldId id="{256 + i}"/>' for i in range(count))
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('ppt/presentation.xml',
            '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            f'<p:sldIdLst>{ids}</p:sldIdLst><p:sldSz cx="{cx}" cy="{cy}"/></p:presentation>')


class RenderGeometryTests(unittest.TestCase):
    def test_two_and_many_pages_have_explicit_bounded_viewports(self):
        with tempfile.TemporaryDirectory() as temp:
            deck = Path(temp) / 'deck.pptx'
            for count in (2, 3, 7, 12, 20):
                with self.subTest(count=count):
                    write_deck(deck, count)
                    geometry = adapter.contact_sheet_geometry(deck)
                    argv = adapter.officecli_command_argv('officecli', 'screenshot', str(deck),
                                                          contact_sheet=True, output='contact.png')
                    self.assertEqual(geometry['slide_count'], count)
                    self.assertEqual(geometry['width'], 1600)
                    self.assertGreaterEqual(geometry['rows'] * geometry['columns'], count)
                    self.assertEqual(argv[argv.index('--grid') + 1], str(geometry['columns']))
                    self.assertEqual(argv[argv.index('--screenshot-width') + 1], str(geometry['width']))
                    self.assertEqual(argv[argv.index('--screenshot-height') + 1], str(geometry['height']))
                    row_height = (geometry['width'] * 9 + geometry['columns'] * 16 - 1) // (geometry['columns'] * 16)
                    self.assertGreaterEqual(geometry['height'], geometry['rows'] * (row_height + 96) + 96)
                    self.assertLessEqual(geometry['width'] * geometry['height'], 32_000_000)
                    self.assertNotIn('--page', argv)

    def test_portrait_uses_actual_dimensions(self):
        with tempfile.TemporaryDirectory() as temp:
            deck = Path(temp) / 'deck.pptx'
            write_deck(deck, 7, 5143500, 9144000)
            geometry = adapter.contact_sheet_geometry(deck)
            self.assertEqual(geometry['slide_width_emu'], 5143500)
            self.assertEqual(geometry['slide_height_emu'], 9144000)
            self.assertGreater(geometry['height'], geometry['width'])

    def test_single_page_argv_is_unchanged_and_needs_no_geometry(self):
        self.assertEqual(adapter.officecli_command_argv('officecli', 'screenshot', 'placeholder.pptx',
                                                       slide=2, output='slide.png'),
                         ['officecli', 'view', 'placeholder.pptx', 'screenshot', '--page', '2', '--out', 'slide.png'])

    def test_proof_subset_does_not_shrink_contact_deck(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'workspace.json').write_text('{}')
            # Deliberately shorter than the actual deck: outline length is not geometry authority.
            (root / 'outline.json').write_text(json.dumps({'slides': [
                {'id': 'opening', 'ordinal': 1}, {'id': 'decision', 'ordinal': 2}]}))
            write_deck(root / 'build/final.pptx', 7)
            resolution = {'path': '/fake/officecli', 'source': 'test', 'version': adapter.PINNED_VERSION}
            with patch.object(render, 'require_pinned_officecli', return_value=resolution):
                full = render.prepare_render_packet(root)
                proof = render.prepare_render_packet(root, slide_ids=['decision'], render_root='renders/style-proof')
            self.assertEqual(proof['slide_ids'], ['decision'])
            self.assertEqual(len(proof['artifacts']), 1)
            self.assertEqual(proof['contact_sheet']['geometry'], full['contact_sheet']['geometry'])
            self.assertEqual(proof['contact_sheet']['geometry']['slide_count'], 7)
            argv = next(a['argv'] for a in proof['actions'] if a['kind'] == 'command' and a['family'] == 'contact-sheet')
            self.assertNotIn('--page', argv)
            self.assertFalse(proof['completion_proof'])
            self.assertTrue(proof['host_image_inspection_required'])

    def test_invalid_geometry_and_large_images_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            deck = Path(temp) / 'deck.pptx'
            for payload in (b'PPTX placeholder',):
                deck.write_bytes(payload)
                with self.assertRaises(adapter.OfficeCLIAdapterError) as caught:
                    adapter.officecli_command_argv('officecli', 'screenshot', str(deck), contact_sheet=True, output='x.png')
                self.assertEqual(caught.exception.code, 'CONTACT_SHEET_GEOMETRY_INVALID')
            for xml in ('<broken', '<presentation/>',
                        '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>'):
                with zipfile.ZipFile(deck, 'w') as archive:
                    archive.writestr('ppt/presentation.xml', xml)
                with self.assertRaises(adapter.OfficeCLIAdapterError):
                    adapter.contact_sheet_geometry(deck)
            for count, cx, cy in ((0, 1, 1), (2, 0, 1), (2, 1, -1)):
                write_deck(deck, count, cx, cy)
                with self.assertRaises(adapter.OfficeCLIAdapterError):
                    adapter.contact_sheet_geometry(deck)
            write_deck(deck, 10000)
            with self.assertRaises(adapter.OfficeCLIAdapterError) as caught:
                adapter.contact_sheet_geometry(deck)
            self.assertEqual(caught.exception.code, 'CONTACT_SHEET_VIEWPORT_TOO_LARGE')


if __name__ == '__main__':
    unittest.main()
