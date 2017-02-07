# REST-API---GMAIL-parser

Below are the steps to be followed in order to use this API
1.	GET request without any domain will show the welcome screen.

2.	POST request has to be sent since we post the username, password, keyword, search_option and content_flag details in order to get the     data.

3.	URL should be ending with ‘/login’ to indicate that login details is being sent.

4.	The values have to be attached as parameters in the body of the POST request.

5.	Parameter names should be username, password, keyword, search_option and content_flag as mentioned in the above screenshot.

6.	If the request is a success, success message is returned else corresponding error message is returned.

7.	Output file will be stored in a directory with the timestamp in its name under the current working directory.

