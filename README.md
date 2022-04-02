# Poopoo

## Workflow

1. Creating a query from random words.
2. Fixing the query to be aligned with the English language using OpenAI.
3. Requesting OpenAI to write a text using query as theme.
4. Translating the result from English.
5. Posting results to Telegram channel.

### 1. Creating a query from random words
Words are taken randomly from the categories of Wiktionary: adjective, verb, noun, adverb.
Style is taken randomly from the appropriate Wikipedia categories.
Format of the query is:

`Write a {genre} about how {adjective} Person {verb} by {noun} and {adverb} sleeps.`

### 2. Fixing the query
Query is fixed by request to OpenAI:

`Correct this to standard English: {query}`