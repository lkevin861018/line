import base64
import hashlib
import hmac
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


# 所有 webhook 都在本機驗簽；LINE、OpenAI、GitHub 與 keep-alive 不會發出網路請求。
with patch.dict(os.environ, {"line_token": "test-token", "line_secret": "test-secret"}):
    with patch("threading.Thread.start"):
        import app as bot


class ChatUiTests(unittest.TestCase):
    def setUp(self):
        self.client = bot.app.test_client()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        roll = root / "roll"
        boyvfv = root / "boyvfv"
        roll.mkdir()
        boyvfv.mkdir()
        for name in ("10_line.png", "2_line.png", "1_line.png", "0_line.gif", "notes.txt"):
            (roll / name).touch()
        for name in ("photo10.jpg", "photo2.jpg", "photo1.jpg"):
            (boyvfv / name).touch()
        for target, value in (("ROLL_DIR", roll), ("BOYVFV_DIR", boyvfv)):
            patcher = patch.object(bot, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        api_patcher = patch.object(bot, "line_bot_api")
        self.api = api_patcher.start()
        self.addCleanup(api_patcher.stop)
        bot.upload_sessions.clear()
        bot.image_edit_sessions.clear()

    def webhook(self, kind, **payload):
        event = {
            "type": kind, "replyToken": "test-reply-token", "timestamp": 1,
            "source": {"type": "group", "groupId": "group1", "userId": "user1"},
            **payload,
        }
        body = json.dumps({"events": [event]}, ensure_ascii=False)
        signature = base64.b64encode(
            hmac.new(bot.line_secret.encode(), body.encode(), hashlib.sha256).digest()
        ).decode()
        self.api.reply_message.reset_mock()
        result = self.client.post(
            "/callback", data=body, content_type="application/json",
            headers={"X-Line-Signature": signature},
        )
        self.assertEqual(result.status_code, 200)
        self.api.reply_message.assert_called_once()
        self.assertEqual(self.api.reply_message.call_args.args[0], "test-reply-token")
        return self.api.reply_message.call_args.args[1]

    def text(self, text):
        return self.webhook("message", message={"type": "text", "id": "message1", "text": text})

    def postback(self, data):
        return self.webhook("postback", postback={"data": data})

    def gallery_action(self, messages, row, column):
        card = messages[1].as_json_dict()["contents"]
        return card["body"]["contents"][row]["contents"][column]["action"]["data"]

    def test_menu_exposes_every_feature_and_prefills_commands(self):
        menu = self.text("選單")[0].as_json_dict()
        actions = [item["action"] for item in menu["contents"]["footer"]["contents"]]
        self.assertEqual(len(actions), 7)
        self.assertEqual(
            {action.get("text") for action in actions if action["type"] == "message"},
            {"抽", "銀河", bot.UPLOAD_COMMAND},
        )
        self.assertEqual(
            {action["fillInText"] for action in actions if action["type"] == "postback"},
            {"rolltest ", "@GG人 ", "@GG人畫圖 ", "@GG人改圖 "},
        )
        for action in actions:
            if action["type"] == "postback":
                self.assertEqual(action["inputOption"], "openKeyboard")
                response = self.postback(action["data"])
                self.assertEqual(response[0].type, "text")
                self.assertIn("請", response[0].text)
        self.assertLessEqual(len(menu["quickReply"]["items"]), 13)

    def test_follow_shows_menu(self):
        self.assertEqual(self.webhook("follow")[0].type, "flex")

    def test_rolltest_and_navigation_use_numeric_order_and_wrap(self):
        first = self.text("rolltest 1")
        self.assertTrue(first[0].original_content_url.endswith("/roll/1_line.png"))
        second = self.postback(self.gallery_action(first, 1, 1))
        self.assertTrue(second[0].original_content_url.endswith("/roll/2_line.png"))
        last = self.postback(self.gallery_action(second, 1, 1))
        self.assertTrue(last[0].original_content_url.endswith("/roll/10_line.png"))
        wrapped = self.postback(self.gallery_action(last, 1, 1))
        self.assertTrue(wrapped[0].original_content_url.endswith("/roll/1_line.png"))
        previous = self.postback(self.gallery_action(first, 1, 0))
        self.assertTrue(previous[0].original_content_url.endswith("/roll/10_line.png"))

    def test_old_cards_keep_their_own_position_and_gallery(self):
        first = self.text("rolltest 1")
        self.text("rolltest 10")
        self.text("銀河")
        result = self.postback(self.gallery_action(first, 1, 1))
        self.assertTrue(result[0].original_content_url.endswith("/roll/2_line.png"))

    def test_boyvfv_navigation_stays_in_its_gallery(self):
        with patch.object(bot.rd, "choice", side_effect=lambda images: images[0]):
            first = self.text("銀河")
            second = self.postback(self.gallery_action(first, 1, 1))
            self.assertTrue(second[0].original_content_url.endswith("/boyvfv/photo2.jpg"))
            again = self.postback(self.gallery_action(second, 2, 0))
            self.assertTrue(again[0].original_content_url.endswith("/boyvfv/photo1.jpg"))

    def test_random_roll_uses_existing_numbered_pngs(self):
        with patch.object(bot.rd, "choice", side_effect=lambda images: images[-1]) as choice:
            messages = self.text("抽")
        self.assertEqual([path.name for path in choice.call_args.args[0]],
                         ["1_line.png", "2_line.png", "10_line.png"])
        self.assertTrue(messages[0].original_content_url.endswith("/roll/10_line.png"))
        self.assertIn("3 / 3", messages[1].as_json_dict()["contents"]["body"]["contents"][0]["text"])

    def test_single_image_gallery_wraps_to_itself(self):
        (bot.BOYVFV_DIR / "photo2.jpg").unlink()
        (bot.BOYVFV_DIR / "photo10.jpg").unlink()
        first = self.text("銀河")
        for column in (0, 1):
            result = self.postback(self.gallery_action(first, 1, column))
            self.assertEqual(first[0].original_content_url, result[0].original_content_url)

    def test_missing_or_empty_gallery_returns_help(self):
        with patch.object(bot, "BOYVFV_DIR", Path(self.temp.name) / "missing"):
            self.assertIn("目前沒有", self.text("銀河")[0].text)
        for path in bot.ROLL_DIR.iterdir():
            path.unlink()
        self.assertIn("目前沒有", self.text("抽")[0].text)

    def test_removed_image_and_out_of_range_number_return_help(self):
        first = self.text("rolltest 1")
        (bot.ROLL_DIR / "1_line.png").unlink()
        self.assertIn("已不存在", self.postback(self.gallery_action(first, 1, 1))[0].text)
        self.assertIn("已不存在", self.text("rolltest 999")[0].text)
        self.assertIn("請輸入", self.text("rolltest abc")[0].text)

    def test_malformed_and_path_traversal_postbacks_are_safe(self):
        for data in ("invalid", "[]", "null", '{"action":"prompt","command":[]}',
                     '{"action":"browse","category":[],"direction":"next","file":"1_line.png"}',
                     '{"action":"browse","category":"roll","direction":"delete","file":"1_line.png"}'):
            with self.subTest(data=data):
                self.assertIn("操作已失效", self.postback(data)[0].text)
        result = self.postback(json.dumps({
            "action": "browse", "category": "roll", "direction": "next", "file": "../secret.png",
        }))
        self.assertIn("已不存在", result[0].text)

    def test_upload_and_edit_offer_photo_picker_and_keep_existing_sessions(self):
        for command, sessions in (
            (bot.UPLOAD_COMMAND, bot.upload_sessions),
            ("@GG人改圖 把背景改成海邊", bot.image_edit_sessions),
        ):
            result = self.text(command)[0].as_json_dict()
            self.assertEqual(result["quickReply"]["items"][0]["action"]["type"], "cameraRoll")
            self.assertIn("group1", sessions)
        self.assertNotIn("group1", bot.upload_sessions)

    def test_existing_ai_commands_still_dispatch_and_include_buttons(self):
        with patch.object(bot.ggopenai, "cgpt", return_value="測試回覆") as chat:
            message = self.text("@GG人 你好")[0]
            chat.assert_called_once_with(ask="你好")
            self.assertEqual(message.text, "測試回覆")
            self.assertIsNotNone(message.quick_reply)
        with patch.object(bot.ggopenai, "igpt", return_value="generated/test.png") as draw:
            message = self.text("@GG人畫圖 海邊的貓")[0]
            draw.assert_called_once_with("海邊的貓")
            self.assertTrue(message.original_content_url.endswith("/generated/test.png"))

    def test_bad_signature_is_rejected_before_postback_dispatch(self):
        result = self.client.post(
            "/callback", json={"events": []}, headers={"X-Line-Signature": "invalid"},
        )
        self.assertEqual(result.status_code, 400)
        self.api.reply_message.assert_not_called()


if __name__ == "__main__":
    unittest.main()
