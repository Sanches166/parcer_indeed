import io
import re
import docx2txt
import requests
import headers


def parser(response):
    content_type = response.headers['Content-Type']
    if content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        text = transform(response.content)
    elif content_type == 'text/plain':
        text = response.text
    else:
        raise RuntimeError(f'Undefined type {content_type}')

    email_match = re.search(r'\S+@\S+\.\S+', text)
    if email_match:
        email = email_match.group()
        # print("Email:", email)
    else:
        cand_id = re.search(r'id=([0-9a-fA-F]{12})', response.request.url).group(1)
        email = fetch_indeed_email(cand_id, response.request._cookies)
        # print("Email не найден в тексте")
    return email

def transform(data):
    virtual_file = io.BytesIO(data)
    text = docx2txt.process(virtual_file)
    return text
        
def fetch_indeed_email(cand_id, cookie):
    json_data = {
    'operationName': 'CandidateSubmissionsMultiple',
    'variables': {
        'input': {
            'legacyIds': [
                cand_id
            ],
        },
    },
    'query': 'query CandidateSubmissionsMultiple($input: CandidateSubmissionsInput!) {\n  candidateSubmissions(input: $input) {\n    ...CandidateSubmissionFragment\n    __typename\n  }\n}\n\nfragment CandidateSubmissionFragment on CandidateSubmissionsPayload {\n  results {\n    id\n    data {\n      ... on EmployerGeneratedCandidateSubmission {\n        legacyID\n        __typename\n      }\n      ... on HiddenEmployerGeneratedCandidateSubmission {\n        legacyID\n        __typename\n      }\n      ... on HiddenIndeedApplyCandidateSubmission {\n        legacyID\n        __typename\n      }\n      ... on IndeedApplyCandidateSubmission {\n        legacyID\n        empAssistExpirationTimestamp\n        __typename\n      }\n      activity {\n        ... on CandidateSubmissionRejectionLetterActivity {\n          status\n          __typename\n        }\n        ... on CandidateSubmissionWithdrawActivity {\n          actor {\n            type\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      candidateIdentity {\n        candidateId\n        jobseekerAccountKey\n        candidate {\n          id\n          submissionsConnection {\n            submissions {\n              id\n              data {\n                jobs {\n                  jobs {\n                    id\n                    jobData {\n                      id\n                      country\n                      title\n                      dateCreated\n                      location {\n                        formatted {\n                          short\n                          __typename\n                        }\n                        __typename\n                      }\n                      ... on HostedJobPost {\n                        id\n                        legacyId\n                        __typename\n                      }\n                      __typename\n                    }\n                    __typename\n                  }\n                  __typename\n                }\n                ... on EmployerGeneratedCandidateSubmission {\n                  legacyID\n                  __typename\n                }\n                ... on HiddenEmployerGeneratedCandidateSubmission {\n                  legacyID\n                  __typename\n                }\n                ... on HiddenIndeedApplyCandidateSubmission {\n                  legacyID\n                  __typename\n                }\n                ... on IndeedApplyCandidateSubmission {\n                  legacyID\n                  __typename\n                }\n                created\n                milestone {\n                  milestone {\n                    category\n                    milestoneId\n                    __typename\n                  }\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      created\n      feedback(first: 100000) {\n        feedback {\n          id\n          created\n          createdBy {\n            id\n            employer {\n              id\n              name\n              __typename\n            }\n            __typename\n          }\n          ... on EmployerCandidateComment {\n            feedbackText\n            __typename\n          }\n          ... on EmployerCandidateFeedback {\n            feedbackText\n            __typename\n          }\n          ... on EmployerCandidateSentiment {\n            interestLevel\n            __typename\n          }\n          metaData {\n            candidateSource {\n              event {\n                name\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      jobs {\n        jobs {\n          id\n          jobData {\n            id\n            location {\n              formatted {\n                short\n                __typename\n              }\n              __typename\n            }\n            company\n            title\n            ... on HostedJobPost {\n              id\n              legacyId\n              title\n              location {\n                countryCode\n                formatted {\n                  short\n                  __typename\n                }\n                __typename\n              }\n              language\n              advertisingLocations {\n                publicJobPageUrl\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      metadata {\n        data {\n          ... on CandidateEmploymentHistory {\n            jobTitle\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      milestone {\n        milestone {\n          milestoneId\n          category\n          __typename\n        }\n        startTime\n        __typename\n      }\n      profile {\n        name {\n          displayName\n          __typename\n        }\n        contact {\n          phoneNumber\n          email: aliasedEmail\n          __typename\n        }\n        location {\n          location\n          country\n          __typename\n        }\n        __typename\n      }\n      resume {\n        ... on CandidatePdfResume {\n          id\n          __typename\n        }\n        ... on CandidateHtmlFile {\n          id\n          __typename\n        }\n        ... on CandidateTxtFile {\n          id\n          __typename\n        }\n        ... on CandidateUnrenderableFile {\n          id\n          __typename\n        }\n        __typename\n      }\n      sources {\n        sourceId\n        sourceType\n        __typename\n      }\n      supportingFiles {\n        attachments {\n          ... on CandidateHtmlFile {\n            body\n            downloadUrl\n            id\n            name\n            __typename\n          }\n          ... on CandidateTxtFile {\n            body\n            downloadUrl\n            id\n            name\n            __typename\n          }\n          ... on CandidateUnrenderableFile {\n            name\n            id\n            downloadUrl\n            __typename\n          }\n          ... on CandidatePdfFile {\n            downloadUrl\n            id\n            name\n            __typename\n          }\n          __typename\n        }\n        coverLetter {\n          ... on CandidateHtmlFile {\n            body\n            name\n            id\n            downloadUrl\n            __typename\n          }\n          ... on CandidateTxtFile {\n            body\n            name\n            id\n            downloadUrl\n            __typename\n          }\n          ... on CandidateUnrenderableFile {\n            name\n            id\n            downloadUrl\n            __typename\n          }\n          ... on CandidatePdfFile {\n            name\n            id\n            downloadUrl\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      submissionUuid\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n',
}
    params = {
    'locale': 'ru',
}

    response = requests.post('https://apis.indeed.com/graphql', params=params, cookies=cookie, headers=headers.graph, json=json_data)
    
    email = response.json().get('data', {}).get('candidateSubmissions', {}).get('results', [{}])[0].get('data', {}).get('profile', {}).get('contact', {}).get('email')
    return email