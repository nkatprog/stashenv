# stashenv

> CLI tool to securely store and switch between named `.env` profiles per project.

---

## Installation

```bash
pip install stashenv
```

---

## Usage

```bash
# Save the current .env as a named profile
stashenv save production

# List all saved profiles
stashenv list

# Switch to a saved profile
stashenv use staging

# Delete a profile
stashenv delete old-profile
```

Profiles are stored encrypted on your local machine and are scoped to each project directory.

---

## Why stashenv?

Managing multiple `.env` files across environments (dev, staging, production) is messy and error-prone. `stashenv` lets you name, store, and swap them instantly without ever committing secrets to version control.

---

## Requirements

- Python 3.8+
- Works on macOS, Linux, and Windows

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the [MIT License](LICENSE).