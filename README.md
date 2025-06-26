# Boto3 Route53 Automations

A Python-based automation toolkit for managing AWS Route 53 DNS records and hosted zones. This project provides a set of utilities and scripts to streamline common Route 53 operations using the AWS SDK (boto3).

## Features

- Create and manage Route 53 hosted zones
- Create, update, and delete DNS records
- List hosted zones and DNS records
- Batch operations for managing multiple DNS records
- Error handling and logging
- Rate limiting for API requests
- Support for both public and private hosted zones

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tzervas/boto3-r53-automations.git
cd boto3-r53-automations
```

2. Set up a Python virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
uv pip install -r requirements.txt
```

3. Configure AWS credentials:
- Either set up AWS credentials in `~/.aws/credentials`
- Or set environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

## Usage

### Creating a Hosted Zone

```python
from scripts.create_hosted_zone import create_hosted_zone

create_hosted_zone("example.com")
```

### Managing DNS Records

```python
from src.session_manager import SessionManager
from src.route53_client import Route53Client
from src.route53_operations import Route53Operations

# Initialize the Route53 client
session = SessionManager().get_session()
client = Route53Client(session).get_client()
route53 = Route53Operations(client)

# Create DNS records
route53.create_dns_record(
    hosted_zone_id="Z1234567890",
    domain="example.com",
    load_balancer_ip="10.0.0.1",
    services=["api", "web"]
)

# List records in a hosted zone
records = route53.list_records("Z1234567890")

# Delete DNS records
route53.delete_dns_records(
    hosted_zone_id="Z1234567890",
    domain="example.com",
    services=["api", "web"]
)
```

## Project Structure

```
├── scripts/                 # Standalone scripts for common operations
│   ├── create_hosted_zone.py
│   ├── create_record.py
│   ├── delete_record.py
│   ├── list_hosted_zones.py
│   ├── list_records.py
│   └── update_record.py
├── src/                    # Core functionality
│   ├── records.py
│   ├── route53_client.py
│   ├── route53_operations.py
│   ├── session_manager.py
│   └── utils/
│       ├── error_handling.py
│       ├── logging.py
│       └── rate_limiter.py
└── tests/                  # Unit tests
```

## Development

This project follows Python best practices and uses the following tools:

- Black for code formatting
- pytest for testing
- Type hints for better code quality
- Comprehensive error handling
- Detailed logging

### Running Tests

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Tyler Zervas