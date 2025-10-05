from tiktoken import get_encoding
import json

encoding = get_encoding("cl100k_base")  # Use cl100k_base for Gemma 2B Q4

json_obj = {
    "org_related": True,
    "has_context": True,
    "answer": "To avail of advance salary, you need to complete at least one year of service with Techmojo Solutions Pvt Ltd. You need to email HR (kalyani@techmojo.in) with your request.  Please note that you need to mention the reason for seeking advance salary.  We will process the request within on or before 10 working days.  Post the approval, you will receive an email from HR seeking 5 HDFC templates with the file attachment http://surl.li/cbngu.  Techmojo never charge any loan interest on this amount. Please note this policy is created for employee benefit. Kindly note, Techmojo will provide Advance salary of max one lakh rupees only. This amount will be deducted from an employee from your monthly salary in 4 to 5 instalments with a 20 to 25k per month deduction. All such information you should provide in the attached file.",
    "dept": "HR",
    "followup": "Is there anything else you'd like to know about Techmojo Solutions Pvt Ltd's advance salary policy?",
    "std_question": ""
}

json_str = json.dumps(json_obj)
tokens = encoding.encode(json_str)
print("Token count:", len(tokens))

