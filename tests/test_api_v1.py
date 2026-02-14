import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import create_app


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xa6\xb9\xa5\x00\x00\x00\x00IEND\xaeB`\x82"
)


class ApiV1TestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.library_root = self.root / "library"
        self.book_rel = "cosmere/nacidos-de-la-bruma-era-1/el-imperio-final"
        self.story_rel = f"{self.book_rel}/01"
        self.story_file = self.library_root / self.book_rel / "01.json"
        self.seed_image = self.library_root / self.book_rel / "img_seed_seed.png"

        self.story_file.parent.mkdir(parents=True, exist_ok=True)
        self.seed_image.write_bytes(PNG_1X1)

        payload = {
            "schema_version": "1.0",
            "story_id": "01",
            "title": "Historia de prueba",
            "status": "ready",
            "book_rel_path": self.book_rel,
            "created_at": "2026-02-14T10:00:00+00:00",
            "updated_at": "2026-02-14T10:00:00+00:00",
            "pages": [
                {
                    "page_number": 1,
                    "status": "draft",
                    "text": {"original": "texto original", "current": "texto current"},
                    "images": {
                        "main": {
                            "slot_name": "main",
                            "status": "draft",
                            "prompt": {
                                "original": "prompt original",
                                "current": "prompt current",
                            },
                            "active_id": "seed-alt",
                            "alternatives": [
                                {
                                    "id": "seed-alt",
                                    "slug": "seed",
                                    "asset_rel_path": f"library/{self.book_rel}/img_seed_seed.png",
                                    "mime_type": "image/png",
                                    "status": "candidate",
                                    "created_at": "2026-02-14T10:00:00+00:00",
                                    "notes": "seed",
                                }
                            ],
                        }
                    },
                }
            ],
        }
        self.story_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        self.patchers = [
            patch("app.config.ROOT_DIR", self.root),
            patch("app.config.LIBRARY_ROOT", self.library_root),
            patch("app.story_store.ROOT_DIR", self.root),
            patch("app.story_store.LIBRARY_ROOT", self.library_root),
            patch("app.routes_api_v1.LIBRARY_ROOT", self.library_root),
        ]

        for patcher in self.patchers:
            patcher.start()

        app = create_app()
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        for patcher in reversed(self.patchers):
            patcher.stop()
        self.tempdir.cleanup()

    def test_api_v1_library_node_root(self):
        response = self.client.get("/api/v1/library/node?path=")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["data"]["node"]["path_rel"], "")
        self.assertGreaterEqual(len(payload["data"]["children"]), 1)

    def test_api_v1_library_node_filters_local(self):
        response = self.client.get(
            "/api/v1/library/node",
            query_string={
                "path": self.book_rel,
                "kind": "story",
                "status": "ready",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()

        self.assertEqual(len(payload["data"]["children"]), 1)
        item = payload["data"]["children"][0]
        self.assertEqual(item["node_type"], "story")
        self.assertEqual(item["story"]["status"], "ready")

    def test_api_v1_story_page_payload(self):
        response = self.client.get(f"/api/v1/stories/{self.story_rel}", query_string={"p": 999})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()["data"]

        self.assertEqual(payload["pagination"]["selected_page"], 1)
        self.assertEqual(payload["page"]["text"]["current"], "texto current")
        main_slot = next(slot for slot in payload["page"]["slots"] if slot["slot_name"] == "main")
        self.assertTrue(main_slot["definitive_image_url"])

    def test_api_v1_patch_page_updates_current_text(self):
        response = self.client.patch(
            f"/api/v1/stories/{self.story_rel}/pages/1",
            json={
                "text_current": "texto actualizado",
                "main_prompt_current": "prompt actualizado",
            },
        )
        self.assertEqual(response.status_code, 200)

        reloaded = json.loads(self.story_file.read_text(encoding="utf-8"))
        self.assertEqual(reloaded["pages"][0]["text"]["current"], "texto actualizado")
        self.assertEqual(reloaded["pages"][0]["images"]["main"]["prompt"]["current"], "prompt actualizado")

    def test_api_v1_upload_alternative_and_activate(self):
        upload_response = self.client.post(
            f"/api/v1/stories/{self.story_rel}/pages/1/slots/main/alternatives",
            data={
                "image_file": (io.BytesIO(PNG_1X1), "nuevo.png"),
                "alt_slug": "nuevo",
                "alt_notes": "nota",
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(upload_response.status_code, 201)
        upload_payload = upload_response.get_json()["data"]

        main_slot = next(slot for slot in upload_payload["page"]["slots"] if slot["slot_name"] == "main")
        uploaded = next(item for item in main_slot["alternatives"] if item["slug"] == "nuevo")

        activate_response = self.client.put(
            f"/api/v1/stories/{self.story_rel}/pages/1/slots/main/active",
            json={"alternative_id": uploaded["id"]},
        )
        self.assertEqual(activate_response.status_code, 200)

        activate_payload = activate_response.get_json()["data"]
        main_slot_after = next(slot for slot in activate_payload["page"]["slots"] if slot["slot_name"] == "main")
        self.assertEqual(main_slot_after["active_id"], uploaded["id"])

    def test_api_v1_invalid_slot_returns_400(self):
        response = self.client.put(
            f"/api/v1/stories/{self.story_rel}/pages/1/slots/tertiary/active",
            json={"alternative_id": "seed-alt"},
        )
        self.assertEqual(response.status_code, 400)
        payload = response.get_json()
        self.assertEqual(payload["error"]["code"], "invalid_slot")


if __name__ == "__main__":
    unittest.main()
