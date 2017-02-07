from flask import Flask,request,jsonify,Response,abort
import os,sys,getpass,imaplib,email,email.header,re,time

app = Flask(__name__)

def response(status,code,data):
    resp_data = {
    'STATUS':status,
    'DATA':data
        }
    response = jsonify(resp_data)
    response.status_code = code
    return response
 
 
def success(code, data):
    return response("SUCCESS",code, data)
 
def failure(code,data):
    return response("FAILURE",code,data)
 
 
def createdir():
    datetime = time.strftime("%c") #calculate timestamp
    tstmp = re.sub('[:/ ]', '_', datetime)
    tstmp = "output_"+tstmp
    os.mkdir(tstmp)
    file = open(os.path.join(tstmp,"output.txt"),'a')
    return file,tstmp

def content_data(content,file):
    try:  
        if content.is_multipart(): 
                for block in content.walk(): #to parse through each payload available in the content area
                    #get the content type and charset of a particular payload
                    file.write("\n\nCONTENT-TYPE = %s; CONTENT-CHARSET = %s" %(block.get_content_type(),block.get_content_charset()))
                    if block.get_content_charset() == None or block.get_content_charset() == 'None': #if content_charset is None then content is skipped and won't get printed 
                        text = block.get_payload(decode=True)
                        continue

                    else: # content is printed only if the content is in "html" or "text" format
                        charset = block.get_content_charset()
                        if str(block.get_content_type())== 'text/plain':
                            #decode the payload with the provided charset and encode it in 'utf-8'
                            text = unicode(block.get_payload(decode=True), str(charset), "ignore").encode('utf-8', 'replace')
                            file.write("\nCONTENT\n")
                            file.write("---------------------------------------------------------------------------------------\n")
                            file.write("%s" %(text.strip()))
                            file.write("\n\n\n\n\n")
                        elif (block.get_content_type()=='text/html'):
                            html = unicode(block.get_payload(decode=True), str(charset), "ignore").encode('utf-8', 'replace')
                            file.write("\nCONTENT\n")
                            file.write("---------------------------------------------------------------------------------------\n")
                            file.write("%s" %(html.strip()))
                            file.write("\n\n\n\n\n")
        else:
            #if it is not multipart then it is directly decoded with the provided charset and encoded in 'utf-8'
            file.write("\n\nCONTENT-TYPE = %s; CONTENT-CHARSET = %s\n" %(content.get_content_type(),content.get_content_charset()))
            file.write("CONTENT\n")
            file.write("---------------------------------------------------------------------------------------\n")
            if content.get_content_charset():
                text = unicode(content.get_payload(decode=True), content.get_content_charset(), "ignore").encode('utf-8', 'replace')
            else:
                text = content.get_payload(decode=True)
            file.write("%s" %(text.strip()))
            file.write("\n\n\n\n\n")
    except email.errors.MessageError:
        raise Exception("Error in performing operations on the body content")


def header_parser(header,value,param,file):
#check for the availability of the parameter in the header and process it only if it is present
    if (str(email.header.decode_header(header[value])).split("'")[1]) != 'None':
        #to check the priority flag and write the value of the flag
        if param == "PRIORITY" and str(email.header.decode_header(header[value])).split("'")[1] == '1':
            file.write("%s:\tHIGH\n" %(param))
        elif param == "PRIORITY" and str(email.header.decode_header(header[value])).split("'")[1] == '3':
            file.write("%s:\tNORMAL\n" %(param))        
        elif param == "PRIORITY" and str(email.header.decode_header(header[value])).split("'")[1] == '5':
            file.write("%s:\tLOW\n" %(param))   
        else:
            file.write("%s:\t%s\n" %(param,str(email.header.decode_header(header[value])).split("'")[1]))

def header_data(header,msg_flags,file):
    try:
        #retrieve 'subject' value from the header and join the parts if it got split
        subject = email.header.decode_header(header['Subject'])
        subject = ''.join([ part[0].decode('utf-8').encode('utf-8', errors='replace') for part in subject ])
        #retrieve other importanat parameters from the header data and write it in the output file
        content_type = str(email.header.decode_header(header['Content-Type'])).split("'")[1].split(";")[0]
        date = str(email.header.decode_header(header['Date'])).split("'")[1] 
        
        file.write("SUBJECT:\t%s\n" %(subject))
        file.write("DATE:\t%s\n" %(date))

        sender = header_parser(header,"Sender","SENDER",file) or header_parser(header,"From","SENDER",file)
        xsender = header_parser(header,"X-Sender","X-SENDER",file)
        priority = header_parser(header,"X-Priority","PRIORITY",file)

        file.write("CONTENT-TYPE:\t%s\n" %(content_type))

        for flag in msg_flags:
                flag = str(imaplib.ParseFlags(flag)).replace("\\","")[1:-1]
                file.write("FLAGS:\t%s\n" %(flag))

    except email.errors.MessageError:
        raise Exception("Encountered error in decoding the header data")


def write_output(content_flag,file,value,msg_flags,header,content):
    try:
        file.write("\n\n-------------HEADER DATA of EMAIL ID - %s------------\n" %(value))
        header_data(header,msg_flags,file) #function to write the requested header fields in to output file
        file.write("\n-------------END OF HEADER DATA - %s------------\n\n" %(value))
        if content_flag == '1':
            file.write("\n-------------BODY DATA of EMAIL ID - %s------------\n" %(value))
            content_data(content,file) #function to write the body content in to output file
            file.write("\n-------------END OF BODY DATA - %s------------\n\n" %(value))
    except:
        raise Exception("Error in performing write operations on the file")

def retrieve_data(IMAP,data,content_flag,file):
    for value in data[0].split():
        try:
            msg_hstatus,msg_header = IMAP.fetch(value,'(BODY.PEEK[HEADER])') # fetching the header part of the message
            msg_tstatus,msg_text = IMAP.fetch(value,'(RFC822)') #fetching the entire message from which the body content will be filtered
            msg_fstatus,msg_flags = IMAP.fetch(value,'(FLAGS)') #retreiving the flag content of the message
            if msg_hstatus != 'OK' or msg_tstatus != 'OK' or msg_fstatus != 'OK':
                print "Error in fetching the data of Email ID: ",value
                continue
        except imaplib.IMAP4.error:
            raise Exception("Error in performing IMAP fetch operation. Please try after sometime.")
        try:
            header = email.message_from_string(msg_header[0][1]) #using the email module to convert message header in to pretty format for processing
            content = email.message_from_string(msg_text[0][1]) #using the email module to convert message content in to pretty format for processing
        except email.errors.MessageError:
            raise Exception("Error with the email module in reading the messages.")
        write_output(content_flag,file,value,msg_flags,header,content) #function being called to write output in to a file.
    file.close()



def search_mails(IMAP,keyword): #Selected mailbox is searched with the keywords in query format
    status,data = IMAP.search(None,keyword)
    if status!= 'OK':
        raise Exception("Error in performing the search operation on the mailbox.")
    else:
        return data 

def parser_input(IMAP,key_input,opt): #input keywords are converted in to a query format accepted by the IMPAP search()
    keyword = key_input.replace(',','" SUBJECT "')
    if opt=='1':
        keyword = '(SUBJECT "'+keyword+'")' #query format if keywords has to be seached with AND condition between them 
    else:
        if "," not in key_input:
            keyword = '(SUBJECT "'+keyword+'")'
        else:
            keyword = '(OR SUBJECT "'+keyword+'")' #query format if keywords has to be seached with OR condition between them 
    return keyword

@app.route('/')
def welcome():
    user = getpass.getuser()
    welcome = '''
 
:::       ::: :::::::::: :::         ::::::::   ::::::::  ::::    ::::  ::::::::::
:+:       :+: :+:        :+:        :+:    :+: :+:    :+: +:+:+: :+:+:+ :+:      
+:+       +:+ +:+        +:+        +:+        +:+    +:+ +:+ +:+:+ +:+ +:+      
+#+  +:+  +#+ +#++:++#   +#+        +#+        +#+    +:+ +#+  +:+  +#+ +#++:++# 
+#+ +#+#+ +#+ +#+        +#+        +#+        +#+    +#+ +#+       +#+ +#+      
 #+#+# #+#+#  #+#        #+#        #+#    #+# #+#    #+# #+#       #+# #+#      
  ###   ###   ########## ##########  ########   ########  ###       ### ##########
 
*****************************************************************************
                  GMAIL Message Parser API  v1.0                                                                                                                           
                                                                               
                Results will be in the output_"timestamp" directory under                           
                                                the current working directory                                                                                                                   
                                                                                                                                                                                                                                                                                                                               
*****************************************************************************
 
"Hi %s !!!! Hope you are doing well"
'''%(user)
    return welcome


 
@app.route('/login',methods=['POST'])
def keyword_search():
    try:
        try:
            username = request.form['username']
            password = request.form['password']
            keywords = request.form['keyword']
            key_opt = request.form['search_option']
            content_flag = request.form['content_flag']
        except:
            return failure(500, "Error in accessing the form data.")
        IMAP = imaplib.IMAP4_SSL('imap.gmail.com') #to establish connection over SSL to the IMAP gmail server
        try:
            IMAP.login(username,password)
        except:
            return failure(400, "Bad Request. Username and password seems to be incorrect.")
        status,mailbox = IMAP.select("[Gmail]/All Mail")
        if status != 'OK':
            return failure(500, "Error in opening the mailbox")
        keyword_list = parser_input(IMAP,keywords,key_opt)
        data = search_mails(IMAP,keyword_list)
        file,name = createdir()
        retrieve_data(IMAP,data,content_flag,file)
        return success(200,"Inbox has been parsed for emails with the requested keyword(s) in the subject line and the output file is present under the path "+name+'/output.txt in the current working directory')

    except imaplib.IMAP4.error as e:
        return failure(500, e.message)
    except AttributeError as e:
        return failure(500, e.message)
    except IOError:
        return failure(500, "Error with the file operations") 
    except Exception as e:
        return failure(500,e.message)
 
if __name__ == '__main__':
    app.run(port=5000)