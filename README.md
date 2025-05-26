# Donetick Chores Integration for Home Assistant

## Overview

The Donetick Chores Integration connects Home Assistant to your Donetick instance, allowing you to monitor and manage your chores directly within Home Assistant. It creates sensor entities for each chore and button entities to mark them as complete.

## Features

*   **Chore Sensors**: For each chore, a sensor (e.g., `sensor.donetick_chore_feed_the_dogs`) is created.
    *   Displays the status of the chore (e.g., incomplete/complete).
    *   Provides additional details as attributes (e.g., assigned user, due date, notes).
*   **Chore Completion Buttons**: For each chore, a button entity (e.g., `button.complete_feed_the_dogs`) is created to mark the chore as complete.
*   **Dynamic Updates**: Chore statuses are periodically fetched from your Donetick instance.

## Prerequisites

*   A running Home Assistant instance.
*   Access to your Donetick instance, specifically:
    *   The API base URL (e.g., `http://your-donetick-host/api/v1/chore`).
    *   Your Donetick API Secret Key (token).

## Installation

1.  **Copy Files**:
    *   Copy all files from this repository (the `donetick_integration` directory) into your Home Assistant's `custom_components/` directory.
    *   You should have a path like `<home_assistant_config_dir>/custom_components/donetick_integration/`.
2.  **Restart Home Assistant**:
    *   Restart your Home Assistant server to allow it to recognize the new integration.

## Configuration

1.  **Add Integration**:
    *   In Home Assistant, go to **Settings > Devices & Services**.
    *   Click **+ ADD INTEGRATION**.
    *   Search for "Donetick Chores" and select it.
2.  **Enter Details**:
    *   **API URL**: Enter the base URL for your Donetick chores API (e.g., `http://your-donetick-host/api/v1/chore`). This URL should be the direct endpoint that lists your chores when an HTTP GET request is made.
    *   **API Token**: Enter your Donetick API Secret Key.
    *   **(Optional) Name**: Give your Donetick integration instance a unique name if you plan to add multiple instances.
3.  **Submit**:
    *   Click "Submit". The integration will attempt to connect to your Donetick instance and set up the entities.

## Usage

Once configured, the integration will automatically create:

*   **Sensor Entities**: Named like `sensor.donetick_chore_CHORE_ID` (e.g., `sensor.donetick_chore_walk_the_dogs`). You can add these to your dashboard to view chore status and details.
*   **Button Entities**: Named like `button.complete_CHORE_ID` (e.g., `button.complete_walk_the_dogs`). These can be added to your dashboard to mark chores as complete.

### Example Dashboard Configuration

You can use these entities in your Lovelace dashboards. Here's a conceptual example for displaying a chore and its completion button:

```yaml
type: entities
title: My Chores
entities:
  - entity: sensor.donetick_chore_walk_the_dogs
    name: Walk the Dogs
  - entity: button.complete_walk_the_dogs
    name: Complete Walk the Dogs
```

For more advanced dynamic lists, you might explore using cards like `custom:auto-entities` with template rows (refer to community examples for `custom:template-entity-row` to customize display and actions).

## API Interaction

The integration currently interacts with your Donetick API as follows:

*   **Fetching Chores**: It makes a `GET` request to the provided **API URL** to retrieve the list of all chores. This URL itself should return the JSON array of chores.
*   **Completing Chores**: It makes a `POST` request to `{API URL}/complete/{chore_id}` (where `{chore_id}` is the internal ID of the chore) to mark a chore as complete. The `secretkey` header is used for authentication.

Ensure your Donetick instance is configured to support these interactions.

---

_This README was generated to help you get started. Feel free to customize it further!_
