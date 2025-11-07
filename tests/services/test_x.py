import unittest


class Test(unittest.TestCase):

    def test_x(self):
        kwargs = {
            'path_params': {
                'telegram_id': '123'
            }
        }
        url = "/clients/<telegram_id>/detail/"
        path_params = kwargs.get('path_params', {})
        for key in path_params:
            url = url.replace(f"<{key}>", path_params[key])
        self.assertEqual(url, "/clients/123/detail/")


if __name__ == "__main__":
    unittest.main()
