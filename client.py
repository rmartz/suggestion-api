import requests
import random

HOSTNAME = 'http://localhost:8000'


def count(start=0):
    while True:
        yield start
        start += 1


def load_all_data(path, params=None):
    if params is None:
        params = {}

    for page in count(start=1):
        params['page'] = page

        data = load_data(path, params)
        yield from data['results']

        if data['next'] is None:
            return


def load_data(path, params=None):
    url = f"{HOSTNAME}/{path}"
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


def perform_post(path, payload):
    url = f"{HOSTNAME}/{path}"
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def create_voting_session(ballot):
    room = perform_post('room/', {'ballot': ballot['id']})
    session = perform_post('session/', {'room': room['id']})
    return session


def choose_option(options, label_key=None):
    options = list(options)
    while True:
        for i, option in enumerate(options, start=1):
            prompt = option[label_key] if label_key else option
            print(f"{i}: {prompt}")

        value = input("Select an option: ")
        try:
            return options[int(value) - 1]
        except Exception as e:
            print(e)
            print("Please select an option from the list")


def get_suggestions(session):
    options = {
        option['id']: option
        for option in
        load_all_data('ballotoption/', {'ballot': ballot['id']})
    }
    while True:
        data = load_data('suggest', {
            'token': session['id'],
            'mode': random.choice(['explore', 'suggest'])
        })
        yield options[
            data['results'][0]['id']
        ]


def vote_suggestion(session, suggestion, polarity):
    path = f'vote/?token={session["id"]}'
    perform_post(path, {
        'option': suggestion['id'],
        'polarity': polarity
    })


ballot = choose_option(
    load_all_data('ballot/'),
    'label'
)

session = create_voting_session(ballot)

for suggestion in get_suggestions(session):
    print(f'== {suggestion["label"]} ==')
    polarity = choose_option(['Yes', 'No']) == 'Yes'

    vote_suggestion(
        session,
        suggestion,
        polarity
    )

