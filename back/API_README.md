# Ayurveda Article Service API

This document provides an overview of the API endpoints available for the Ayurveda Article Service.

## Base URL
All API endpoints are prefixed with `/api`.

## Endpoints

### 1. Discover Articles
Discover new articles from various sources.

- **URL**: `/articles/discover`
- **Method**: `GET`
- **Query Parameters**:
  - `query` (string, optional): Search query (default: 'Ayurveda')
  - `limit` (number, optional): Maximum number of articles to return (default: 10)

**Example Request**:
```
GET /api/articles/discover?query=Ayurveda&limit=5
```

**Success Response**:
```json
{
  "success": true,
  "count": 5,
  "articles": [
    {
      "title": "The Benefits of Turmeric in Ayurveda",
      "content": "...",
      "source": "Ayurveda Today",
      "url": "https://example.com/turmeric-article",
      "image_url": "https://example.com/turmeric.jpg",
      "published_at": "2023-06-15T10:30:00Z"
    },
    ...
  ]
}
```

### 2. Get Articles
Get a list of published articles with pagination.

- **URL**: `/articles`
- **Method**: `GET`
- **Query Parameters**:
  - `limit` (number, optional): Number of articles per page (default: 10)
  - `offset` (number, optional): Number of articles to skip (default: 0)
  - `sort` (string, optional): Field to sort by (default: 'published_at')
  - `order` (string, optional): Sort order ('asc' or 'desc', default: 'desc')

**Example Request**:
```
GET /api/articles?limit=10&offset=0&sort=published_at&order=desc
```

**Success Response**:
```json
{
  "success": true,
  "count": 10,
  "total": 25,
  "articles": [
    {
      "id": 1,
      "title": "The Benefits of Turmeric in Ayurveda",
      "content": "...",
      "source": "Ayurveda Today",
      "url": "https://example.com/turmeric-article",
      "image_url": "https://example.com/turmeric.jpg",
      "published_at": "2023-06-15T10:30:00Z",
      "view_count": 150,
      "share_count": 25,
      "like_count": 10
    },
    ...
  ]
}
```

### 3. Get Article by ID
Get a single article by its ID.

- **URL**: `/articles/:id`
- **Method**: `GET`
- **URL Parameters**:
  - `id` (number, required): Article ID

**Example Request**:
```
GET /api/articles/1
```

**Success Response**:
```json
{
  "success": true,
  "article": {
    "id": 1,
    "title": "The Benefits of Turmeric in Ayurveda",
    "content": "...",
    "source": "Ayurveda Today",
    "url": "https://example.com/turmeric-article",
    "image_url": "https://example.com/turmeric.jpg",
    "published_at": "2023-06-15T10:30:00Z",
    "view_count": 151,
    "share_count": 25,
    "like_count": 10,
    "category": "Herbs",
    "tags": "turmeric,herbs,anti-inflammatory,digestion"
  },
  "recommendations": [
    {
      "id": 4,
      "title": "Ayurvedic Herbs for Stress Relief",
      "source": "Herbal Remedies",
      "image_url": "https://example.com/herbs-stress.jpg",
      "view_count": 89
    },
    ...
  ]
}
```

### 4. Like an Article
Increment the like count for an article.

- **URL**: `/articles/:id/like`
- **Method**: `POST`
- **URL Parameters**:
  - `id` (number, required): Article ID

**Example Request**:
```
POST /api/articles/1/like
```

**Success Response**:
```json
{
  "success": true,
  "like_count": 11
}
```

### 5. Share an Article
Increment the share count for an article.

- **URL**: `/articles/:id/share`
- **Method**: `POST`
- **URL Parameters**:
  - `id` (number, required): Article ID

**Example Request**:
```
POST /api/articles/1/share
```

**Success Response**:
```json
{
  "success": true,
  "share_count": 26
}
```

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error message describing the issue"
}
```

### Common Status Codes
- `400 Bad Request`: Invalid input parameters
- `404 Not Found`: Requested resource not found
- `500 Internal Server Error`: Server-side error

## Authentication

All endpoints are currently public and do not require authentication. Consider adding authentication for write operations in production.

## Rate Limiting

API is rate-limited to 100 requests per minute per IP address. Exceeding this limit will result in a `429 Too Many Requests` response.

## Versioning

API versioning is handled through the URL path (e.g., `/api/v1/...`). The current version is v1.
