
# Raspberry Pi Ansible User Setup

This guide explains how to prepare your Raspberry Pi for Ansible automation by
creating a dedicated user account with passwordless sudo and SSH key
authentication.

## 1. Initial Access

- Boot your Raspberry Pi and ensure it is connected to your network.
- Find its hostname or IP address (e.g., `raspberrypi.local` or `192.168.x.x`).
- From your control machine, connect using the default `pi` user:

```ini
# For first bootstrap (Password is laptop password)
[raspberrypi]
192.168.68.54 ansible_user=aquilesgomez
# For subsequent commands
[raspberrypi]
192.168.68.54 ansible_user=ansible
```

Future setups are done through `makefiles`,

```sh
make all
# Open this in the browser
http://raspberrypi1.local:5000
```

### Accessing Camera Through Local network

You can access the

## Intent

This is a project that will use a `RaspberryPi` in conjunction with
`homebridge` to control multiple objects around the house.

### Architecture

We will create multiple processes to monitor wand movements and another process
to trigger `homebridge` requests.

```mermaid
sequenceDiagram
    actor a as Child
    box Wand Reader
        participant s as Sensor
        participant mp as Movement Processor
    end
    participant p as plug
    participant h as homebridge
    participant n as Network

    loop Periodically
        s -->> a: Emit IR
    end

    loop Upon IR Receive
        a ->> s: Give wand movement
        s ->> mp: Determine command
        mp ->> n: Make Rest API request to target plug
        n ->> h: Forward Request
        h ->> p: Trigger
    end
```

#### Wand Interaction

The wand interaction needs to have a few moving parts:

- A way to teach it movements
- A way to check taught movements against inputs
- Direct specific movements towards specific API inputs

```mermaid
---
title: Teaching new movements
---
sequenceDiagram
    actor a as Child
    participant c as Camera
    participant r as RaspberryPi

    a -->> c: Training gesture
    c -->> r: Initiate training
    loop Every 10 seconds
        a ->> c: Movement
        c ->> r: Store movement
        r ->> a: Audio queue
    end

```
