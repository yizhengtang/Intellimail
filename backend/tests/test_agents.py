#test_agents.py
#Unit tests for agents.py — tests all six prompt-builder functions and mocks the OpenAI
#client to verify each agent parses and returns the correct output structure.

import json
import pytest
from unittest.mock import MagicMock
import agents
from agents import (
    _build_summarise_prompt,
    _build_categorise_prompt,
    summarize_email,
    categorize_email,
    extract_events,
    generate_reply,
    score_priority,
    is_spam,
)


#Helpers

def _mock_client(content: str) -> MagicMock:
    mock_response = MagicMock()
    mock_response.choices[0].message.content = content
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


#_build_summarise_prompt — pure function

def test_build_summarise_prompt_contains_email_text():
    prompt = _build_summarise_prompt('Meeting at noon', '')
    assert 'Meeting at noon' in prompt
    assert '<email>' in prompt


def test_build_summarise_prompt_without_context_omits_context_block():
    prompt = _build_summarise_prompt('Meeting at noon', '')
    assert '<context>' not in prompt


def test_build_summarise_prompt_with_context_includes_context_block():
    prompt = _build_summarise_prompt('Meeting at noon', 'Past email about meetings')
    assert '<context>' in prompt
    assert 'Past email about meetings' in prompt


#_build_categorise_prompt — pure function

def test_build_categorise_prompt_contains_email_text():
    prompt = _build_categorise_prompt('Your invoice is attached.')
    assert 'Your invoice is attached.' in prompt
    assert '<email>' in prompt


#summarize_email — mocked OpenAI

def test_summarize_email_returns_stripped_summary(monkeypatch):
    monkeypatch.setattr(agents, '_client', _mock_client('  This is the summary.  '))
    result = summarize_email('Full email body here')
    assert result == 'This is the summary.'


def test_summarize_email_passes_context_to_prompt(monkeypatch):
    mock_client = _mock_client('Summary with context.')
    monkeypatch.setattr(agents, '_client', mock_client)
    summarize_email('Email body', context='Related past email')
    call_args = mock_client.chat.completions.create.call_args
    user_content = call_args.kwargs['messages'][1]['content']
    assert 'Related past email' in user_content


#categorize_email — mocked OpenAI

def test_categorize_email_returns_lowercase(monkeypatch):
    monkeypatch.setattr(agents, '_client', _mock_client('  Work  '))
    result = categorize_email('Please review the attached report.')
    assert result == 'work'


def test_categorize_email_normalises_casing(monkeypatch):
    monkeypatch.setattr(agents, '_client', _mock_client('PROMOTIONS'))
    result = categorize_email('50% off sale today only!')
    assert result == 'promotions'


#extract_events — mocked OpenAI

def test_extract_events_returns_list_of_events(monkeypatch):
    events_payload = json.dumps({'events': [
        {'type': 'meeting', 'date': '2025-05-01', 'description': 'Team standup'}
    ]})
    monkeypatch.setattr(agents, '_client', _mock_client(events_payload))
    result = extract_events('Team standup on May 1st at 9am.')
    assert isinstance(result, list)
    assert result[0]['type'] == 'meeting'
    assert result[0]['date'] == '2025-05-01'


def test_extract_events_returns_empty_list_when_no_events(monkeypatch):
    monkeypatch.setattr(agents, '_client', _mock_client(json.dumps({'events': []})))
    result = extract_events('Just a friendly hello, no events here.')
    assert result == []


#generate_reply — mocked OpenAI

def test_generate_reply_returns_draft_string(monkeypatch):
    monkeypatch.setattr(agents, '_client', _mock_client('  Thank you for your email.  '))
    result = generate_reply('Can you send me the report?')
    assert result == 'Thank you for your email.'


#score_priority — mocked OpenAI

def test_score_priority_returns_score_and_reason(monkeypatch):
    payload = json.dumps({'score': 5, 'reason': 'Server is down, immediate action required.'})
    monkeypatch.setattr(agents, '_client', _mock_client(payload))
    result = score_priority('URGENT: Production server is down!')
    assert result['score'] == 5
    assert 'immediate' in result['reason']


def test_score_priority_uses_fallback_on_missing_fields(monkeypatch):
    #GPT returns an empty JSON object — function should use defaults.
    monkeypatch.setattr(agents, '_client', _mock_client(json.dumps({})))
    result = score_priority('Newsletter: This week in tech')
    assert result['score'] == 3
    assert result['reason'] == ''


#is_spam — mocked OpenAI

def test_is_spam_returns_true_for_spam(monkeypatch):
    payload = json.dumps({'is_spam': True, 'confidence': 0.97})
    monkeypatch.setattr(agents, '_client', _mock_client(payload))
    result = is_spam('Congratulations! You have won a prize!')
    assert result['is_spam'] is True
    assert result['confidence'] == 0.97


def test_is_spam_returns_false_for_legitimate_email(monkeypatch):
    payload = json.dumps({'is_spam': False, 'confidence': 0.99})
    monkeypatch.setattr(agents, '_client', _mock_client(payload))
    result = is_spam('Hi, are you free for a call tomorrow?')
    assert result['is_spam'] is False
    assert result['confidence'] == 0.99


def test_is_spam_uses_fallback_on_missing_fields(monkeypatch):
    monkeypatch.setattr(agents, '_client', _mock_client(json.dumps({})))
    result = is_spam('Some email content')
    assert result['is_spam'] is False
    assert result['confidence'] == 0.0
