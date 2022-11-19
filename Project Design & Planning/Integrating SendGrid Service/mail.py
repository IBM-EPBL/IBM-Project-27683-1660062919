sg = SendGridAPIClient('Your API');
message = Mail(
          from_email='vimalsona206@gmail.com',
          to_emails=email,
          subject='Successfully registered at plasma donar website',
          html_content=f'''
            Hi {name}, <br/>
            This is to inform that your slot for donar applicantion has been successfully booked on {slot}. <br/>
            We hope to meet you soon.
            <br/><br/>
            Thank you
          ''')
      try:
          
          response = sg.send(message)
          print(response.status_code)
          print(response.body)
          print(response.headers)
      except Exception as e:
          print(e.message)