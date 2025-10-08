# Parabank-Automation

This project automates the ParaBank sign-up and login flows using Behave (BDD) and the Page Object Model (POM) pattern.
It creates a new user account, signs in with that account, and captures and prints the Total balance displayed on the Accounts Overview page.

---

## Project Structure

* `features/` – Gherkin feature files (for example: `signup_login.feature`).
* `features/steps/` – Step definitions implementing feature steps (`signup_login_steps.py`).
* `pages/` – Page Object classes encapsulating UI locators and actions.
* `utils/` – Utilities such as locator resolution, configuration loader, data factory, and test state management.
* `artifacts/` – Stores screenshots, logs, Allure results, and other execution outputs.
* `config.properties` – Configuration file for environment base URL and test credentials.
* `object_repository/` - Contains a json file containing the locators needed to automate the workflow.
* `drivers/` - Conatins the setup needed on how the web-driver is configured.

---

## Prerequisites

* Python 3.10 or higher
* Google Chrome or Chromium browser installed
* Install project dependencies:

```bash
pip install -r requirements.txt
```

---
## Running Tests
Execute tests with Allure reporting enabled and human-readable output:
```bash
behave -f allure_behave.formatter:AllureFormatter -o allure-results -f pretty
```
---
## Generating Allure Reports
Generate a static HTML report:
```bash
allure generate allure-results -o allure-report --clean
```
Serve the Allure report locally in the browser:
```bash
allure serve allure-results
```
---

## Deliverables

* Test Cases: Documented in Excel file `./docs/Parabank Test Cases.xlsx`
* Automation Code: Available in this repository with BDD and POM implementation.
* Proof of Execution: Screenshots and recordings stored in the root folder.

---

