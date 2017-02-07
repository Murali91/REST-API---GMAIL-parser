from Challenge1_REST import app
import unittest

class FlaskTest(unittest.TestCase):
	def test_keyword_search(self):
		tester = app.test_client(self)
		response = tester.post('/login',data = dict(username = "gapjumpers.test@gmail.com",password="gapjumpers",keyword ="Hours,Not Approved",search_option = 1,content_flag = 1))
		self.assertTrue('Inbox has been parsed for emails with the requested keyword(s) in the subject line and the output file is present under the path' in response.data)



	def test_incorrect_credentials(self):
		tester = app.test_client(self)
		response = tester.post('/login',data = dict(username = "gapjumpers.test@gmail.com",password="gapjumper",keyword ="Hours,Not Approved",search_option = 1,content_flag = 1))
		self.assertTrue('Bad Request. Username and password seems to be incorrect.' in response.data)


	def test_single_keyword(self):
		tester = app.test_client(self)
		response = tester.post('/login',data = dict(username = "gapjumpers.test@gmail.com",password="gapjumpers",keyword="Hour",search_option = 1,content_flag = 1))
		self.assertTrue("Inbox has been parsed for emails with the requested keyword(s) in the subject line and the output file is present under the path" in response.data)

	def test_content_flag(self):
		tester = app.test_client(self)
		response = tester.post('/login',data = dict(username = "gapjumpers.test@gmail.com",password="gapjumpers",keyword ="Hours",search_option = 1,content_flag = 0))
		self.assertTrue("Inbox has been parsed for emails with the requested keyword(s) in the subject line and the output file is present under the path" in response.data)


	def test_search_option(self):
		tester = app.test_client(self)
		response = tester.post('/login',data = dict(username = "gapjumpers.test@gmail.com",password="gapjumpers",keyword ="Hours",search_option = 0,content_flag = 1))
		self.assertTrue("Inbox has been parsed for emails with the requested keyword(s) in the subject line and the output file is present under the path" in response.data)

	def empty_content_flag(self):
		tester = app.test_client(self)
		response = tester.post('/login',data = dict(username = "gapjumpers.test@gmail.com",password="gapjumpers",keyword ="Hours",search_option = 1,content_flag = None))
		self.assertTrue("Inbox has been parsed for emails with the requested keyword(s) in the subject line and the output file is present under the path" in response.data)


	def empty_search_option(self):
		tester = app.test_client(self)
		response = tester.post('/login',data = dict(username = "gapjumpers.test@gmail.com",password="gapjumpers",keyword ="Hours",search_option = None,content_flag = 1))
		self.assertTrue("Inbox has been parsed for emails with the requested keyword(s) in the subject line and the output file is present under the path" in response.data)


if __name__ == '__main__':
    unittest.main()