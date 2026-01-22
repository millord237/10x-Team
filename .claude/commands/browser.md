# /browser

Browser automation command for the 10x Browser Extension. Developed by Team 10x.in.

## Usage

```
/browser [action] [target]
```

## Actions

- `/browser start` - Start browser automation extension
- `/browser linkedin <action>` - LinkedIn browser actions
- `/browser twitter <action>` - Twitter browser actions
- `/browser instagram <action>` - Instagram browser actions
- `/browser track` - View activity tracking dashboard
- `/browser prospects` - Manage prospects (import/export CSV)
- `/browser status` - Check connection and rate limits

## Browser Actions

### LinkedIn
- `view` - View profile
- `connect` - Send connection request
- `message` - Send message
- `like` - Like posts
- `comment` - Comment on posts

### Twitter
- `follow` - Follow user
- `dm` - Send direct message
- `like` - Like tweets
- `retweet` - Retweet
- `reply` - Reply to tweet

### Instagram
- `follow` - Follow user
- `dm` - Send direct message
- `like` - Like posts
- `comment` - Comment on posts

## Quick Examples

```bash
/browser start
/browser linkedin view "https://linkedin.com/in/username"
/browser twitter follow "@username"
/browser track
```

## Extension Installation

1. Open Chrome → Extensions → Developer mode
2. Click "Load unpacked"
3. Select `browser-extension` folder

## Rate Limits

| Platform | Connections/Day | Messages/Day |
|----------|----------------|--------------|
| LinkedIn | 15             | 40           |
| Twitter  | 50 follows     | 20 DMs       |
| Instagram| 50 follows     | 30 DMs       |

---
Developed by Team 10x.in
