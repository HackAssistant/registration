# Open registration

You will only be able to register if applications are open. 

To open registration change the `HACKATHON_APP_DEADLINE` variable in [app/hackathon_variables.py](app/hackathon_variables.py)

# Review applications

1. Register using your hackathon email (ex: `*@hackupc.com`).
2. Confirm your email (you should have gotten a confirmation email)
3. Open registration platform again.

## INTERNAL: How to make a normal user into a volunteer/reviewer

1. Log in your admin account created in the first step from set up (see [README](README.md)). 
2. Access `Admin` tab (see top bar)
3. Go to `User` page (see side bar)
4. Find user you need to change.
5. Go to `Permissions` tab
6. Check the Organizer (for reviews), Volunteer (for checkin) or Director (for invites) boxes.
7. Save user

# Review mechanism

This is a suggested mechanism for reviewing applications. This is used by default. You can change the score system and weight in the code if need to change.

The criteria are also suggestions, feel free to change them at any time.

## Score calculation
The above specified scores can be summed up in 2 (1-10) separate values:

**TECHNICAL SKILLS**. How the hacker is prepared from a technical point of view to participate in this hackathon. This may include:
- Projects he has worked on question 
- Information such as github, CV, linkedin…
- Background: What has the hacker done before (internships…)

**PERSONAL SKILLS**. How the hacker is prepared from a personal point of view to participate in this hackathon. This may include:
- Level of dedication to fill the application (are answers to “most excited about HackCU” and “projects you have collaborated with” well developed/well explained?)
- Correctness/politeness (i.e. no “I want free food” stuff)
- General valoration in: interest in learning, collaborating...

If hacker personally known, reviewer should skip application.

We process this after standardizing votes for each reviewer so that all votes weight similarly. This way we can save votes from people being too kind or too bad.

### Final vote for application
`vote = TECH_SKILLS*0.2+PERSONAL_SKILLS*0.8`


## Batch of invites algorithm

Choose N depending on number of confirmed and invited. From there, order by score. Choose N first ones and invite.  Separate depending if they need travel reimbursement or not (110 reimbursement maximum). Also review independently Spain and UPC applicants to make sure that they get in.
