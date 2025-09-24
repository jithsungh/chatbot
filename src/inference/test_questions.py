# src/inference/test_questions.py
QUESTIONS = [
    # ---------------- HR (10)
    ("How many paid leave days do employees get each year?", "HR"),
    ("Can I carry forward unused vacation days to next year?", "HR"),
    ("What's the process to apply for maternity leave?", "HR"),
    ("How do I update my emergency contact details?", "HR"),
    ("Who handles payroll issues in our company?", "HR"),
    ("Where can I find information about health insurance benefits?", "HR"),
    ("How do I submit documents for my promotion?", "HR"),
    ("Can I change my tax declarations mid-year?", "HR"),
    ("What's the policy for late coming and attendance?", "HR"),
    ("How do I request a letter for visa purposes?", "HR"),

    # ---------------- IT (10)
    ("My laptop screen is flickering — any suggestions?", "IT"),
    ("How do I set up email on my mobile device?", "IT"),
    ("Can you help me install Python on my workstation?", "IT"),
    ("My internet keeps disconnecting during calls.", "IT"),
    ("How do I map a network drive?", "IT"),
    ("Is there a way to restore an accidentally deleted file?", "IT"),
    ("How do I reset my system password?", "IT"),
    ("What should I do if my webcam isn't detected?", "IT"),
    ("How can I connect to the company VPN?", "IT"),
    ("How do I set up a printer on the office network?", "IT"),

    # ---------------- Security (10)
    ("How often should employees change their access PIN?", "Security"),
    ("I lost my ID card — how do I enter the office?", "Security"),
    ("Someone followed me through the entrance door, what should I do?", "Security"),
    ("Is it okay to bring personal USB drives to work?", "IT"),
    ("What's the process to report phishing emails?", "Security"),
    ("Are cameras installed in the parking lot?", "Security"),
    ("What is the policy on sharing building access badges?", "Security"),
    ("Do visitors need to register before entering the office?", "Security"),
    ("How do I request temporary access to a restricted area?", "Security"),
    ("What steps should I take if I notice suspicious activity?", "Security"),

    # ---------------- General Inquiry (10)
    ("Can you recommend a good lunch spot nearby?", "General Inquiry"),
    ("Who won the soccer match last night?", "General Inquiry"),
    ("What's the weather forecast for tomorrow?", "General Inquiry"),
    ("How do I bake a chocolate cake at home?", "General Inquiry"),
    ("What's trending on social media today?", "General Inquiry"),
    ("Which movie is best to watch this weekend?", "General Inquiry"),
    ("What's the capital city of Japan?", "General Inquiry"),
    ("Can you tell me the current stock price of Tesla?", "General Inquiry"),
    ("Where can I find the latest space exploration news?", "General Inquiry"),
    ("Suggest a fun weekend activity.", "General Inquiry"),

    # ---------------- HR (10)
    ("If I take unpaid leave this month, does it reduce my annual leave balance or affect bonuses?", "HR"),
    ("When transferring to another department mid-year, do my leave days reset or carry over?", "HR"),
    ("Can someone request maternity leave retroactively if paperwork was delayed?", "HR"),
    ("If I update my emergency contact online, does HR also get notified automatically?", "HR"),
    ("Who should I contact first: my manager or payroll, if my salary is delayed?", "HR"),
    ("Are mental health benefits included under health insurance, or is it separate?", "HR"),
    ("Do I submit promotion documents before or after my performance review?", "HR"),
    ("If I file new tax declarations, will it automatically update my payroll deductions?", "HR"),
    ("Is tardiness considered per day or per week when calculating attendance penalties?", "HR"),
    ("When requesting a visa letter, should I provide HR with my travel itinerary?", "HR"),

    # ---------------- IT (10)
    ("My laptop freezes only during video calls — should I check network or hardware first?", "IT"),
    ("How do I configure my email on a new phone without losing old messages?", "IT"),
    ("Installing Python breaks another program — how can I resolve conflicts safely?", "IT"),
    ("Internet drops every 10 minutes, but Wi-Fi shows full strength — what next?", "IT"),
    ("I mapped a network drive but can't access certain folders — why?", "IT"),
    ("Deleted files don't appear in Recycle Bin — any recovery options?", "IT"),
    ("I forgot my system password, but am logged in on another device — can I reset remotely?", "IT"),
    ("Webcam works on one app but not others — what troubleshooting steps help?", "IT"),
    ("VPN connects but some internal sites fail to load — what could be wrong?", "IT"),
    ("Printer shows online but prints blank pages — what should I check?", "IT"),

    # ---------------- Security (10)
    ("Is it mandatory to change my access PIN if I suspect someone saw it but didn't report?", "Security"),
    ("I lost my ID card outside office hours — can I enter using temporary pass alone?", "Security"),
    ("Someone tailgates behind me at the door; do I stop them or report first?", "Security"),
    ("Are encrypted USB drives allowed if personal files are stored on them?", "IT"),
    ("If I report a phishing email, does IT or Security take the lead on investigation?", "Security"),
    ("Are parking lot cameras monitored live, or just recorded for later review?", "Security"),
    ("Sharing my building badge with a trusted colleague — is that ever acceptable?", "Security"),
    ("A visitor arrives without registration; should I escort or deny entry?", "Security"),
    ("Temporary access request: do I need manager approval or Security clearance first?", "Security"),
    ("Suspicious activity spotted after hours — should I call Security or police first?", "Security"),

    # ---------------- General Inquiry (10)
    ("Where is the best place for lunch if I want healthy options within walking distance?", "General Inquiry"),
    ("Who scored the winning goal in yesterday's soccer match and at what minute?", "General Inquiry"),
    ("Tomorrow's weather forecast shows rain — should I carry an umbrella or raincoat?", "General Inquiry"),
    ("I want to bake a chocolate cake without eggs — what substitutions work best?", "General Inquiry"),
    ("What's trending on social media right now that's safe for work to share?", "General Inquiry"),
    ("Which movie this weekend is more critically acclaimed vs audience favorite?", "General Inquiry"),
    ("What's the capital city of Japan and its largest metropolitan area?", "General Inquiry"),
    ("Current Tesla stock price is fluctuating — how do I track intraday changes easily?", "General Inquiry"),
    ("Where can I find real-time updates on NASA missions instead of news summaries?", "General Inquiry"),
    ("Suggest a weekend activity that's fun but also budget-friendly.", "General Inquiry"),

    # ---------------- HR (5)
    ("I'm planning to work remotely for a few weeks; do I need formal approval or just notify my manager?", "HR"),
    ("If I switch from part-time to full-time mid-year, how will my benefits and leave days be adjusted?", "HR"),
    ("Are there any restrictions on taking unpaid leave right before a scheduled performance review?", "HR"),
    ("I recently got married — how do I update my spouse's details for insurance coverage?", "HR"),
    ("Can I request a salary advance if I have pending reimbursement claims, or are they processed separately?", "HR"),

    # ---------------- IT (5)
    ("My laptop battery drains unusually fast when using video conferencing apps; should I check settings or hardware?", "IT"),
    ("I'm trying to sync files between cloud storage and my workstation, but changes aren't updating — what could be wrong?", "IT"),
    ("After updating my OS, certain apps crash immediately — how do I roll back safely without losing data?", "IT"),
    ("When connecting to the office VPN from home, some websites load but internal tools don't — what's the likely cause?", "IT"),
    ("I receive error messages when printing from some applications but not others — is this a driver issue or something else?", "IT"),

    # ---------------- Security (5)
    ("I saw someone tailgating but they claimed to be a contractor; should I let them pass or verify credentials first?", "Security"),
    ("If my access badge is demagnetized during work hours, what's the fastest way to regain entry without violating policy?", "Security"),
    ("Are personal devices allowed on the office network if they have updated security software?", "Security"),
    ("I found an unattended USB drive in the parking lot; what's the proper procedure to report it safely?", "Security"),
    ("If I notice suspicious activity on the building perimeter late at night, who should I contact first — Security or local authorities?", "Security"),

    # ---------------- General Inquiry (5)
    ("I'm looking for a quiet cafe near the office that's good for working, any suggestions?", "General Inquiry"),
    ("What are some weekend hiking spots within an hour's drive that aren't too crowded?", "General Inquiry"),
    ("I want to try a new dessert recipe using apples — what options are simple but impressive?", "General Inquiry"),
    ("What's the best way to follow live updates on my favorite sports team without constant notifications?", "General Inquiry"),
    ("I'm planning a short city trip this weekend; what are some must-see spots that are off the usual tourist path?", "General Inquiry"),

    # ---------------- HR (5)
    ("How do I apply for parental leave and what documents are required?", "HR"),
    ("Who should I contact if I have questions about my payroll deductions?", "HR"),
    ("Can I update my emergency contact details online or do I need HR approval?", "HR"),
    ("What’s the procedure for requesting a salary advance or reimbursement?", "HR"),
    ("How do I enroll in or change my health insurance plan?", "HR"),

    # ---------------- IT (5)
    ("My laptop is running very slowly — how can I optimize its performance?", "IT"),
    ("I cannot connect to the VPN from home; what steps should I take?", "IT"),
    ("How do I install company-approved software on my workstation?", "IT"),
    ("My email is not syncing across devices — how do I fix it?", "IT"),
    ("I’m getting an error while printing documents from certain applications — what could be wrong?", "IT"),

    # ---------------- Security (5)
    ("I noticed someone trying to access a restricted area — what should I do?", "Security"),
    ("My access card is not working — who can help me regain entry?", "Security"),
    ("Are personal USB drives allowed on company devices?", "IT"),
    ("How do I report suspicious activity or a security breach?", "Security"),
    ("What is the company policy on tailgating and visitor management?", "Security"),

    # ---------------- General Inquiry (5)
    ("Can you recommend a good place to eat near the office?", "General Inquiry"),
    ("Where can I find the latest news about upcoming tech conferences?", "General Inquiry"),
    ("Who won the recent sports tournament?", "General Inquiry"),
    ("What are some fun team-building activities we can do this weekend?", "General Inquiry"),
    ("Suggest a weekend activity that's fun but also budget-friendly.", "General Inquiry"),

]

