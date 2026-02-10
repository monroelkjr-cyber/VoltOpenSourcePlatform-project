# VoltOpenSourcePlatform-project
Open-source platform for 1st-gen Chevy Volt integrating VCX SE, VIM3, HDMI dashboards, ESP32, Pixhawk, and Comma Two.
3Volt Open Source Platform (VOSP)

Repo: VoltOpenSourcePlatform-project

Executive Summary

This repository houses an open-source hardware–software integration platform for the 1st-generation Chevrolet Volt. The objective is simple and traditional: build a reliable, transparent, and serviceable digital backbone that sits alongside GM’s original systems — not replaces them — and gives engineers, researchers, and builders real visibility into how the car thinks, talks, and behaves.

This is not a toy dashboard. It is a modular instrumentation and data architecture that integrates professional-grade tools into a single, coherent stack.

What This Platform Integrates

The system is built around five core pillars:

VCX SE Pro (DoIP/CAN Gateway)

Enterprise-class vehicle interface

Secure access to GM networks

Bidirectional CAN and diagnostics capability

Khadas VIM3 (Android Automotive HMI Host)

Runs the primary Human–Machine Interface

Drives HDMI displays

Acts as the computing spine for visualization, logging, and control prototypes

HDMI Dashboards

Custom digital cluster displays

Real-time vehicle telemetry

Configurable layouts for testing, validation, and demonstration

ESP32 Edge Nodes

Low-level sensing and peripheral control

Local telemetry collection

Modular expansion for additional instrumentation

Pixhawk + Comma Two (Autonomy Research Stack)

Experimental autonomy interface

High-rate sensor fusion and computer vision

Research pathway toward advanced driver assistance exploration

Scope — what this is and is not

This platform IS:

A research and development environment

A diagnostic and telemetry framework

A proving ground for Volt instrumentation

A transparent alternative to black-box OEM tools

This platform is NOT:

A production replacement for GM modules

A consumer plug-and-play product

A warranty-safe aftermarket device

A fully autonomous driving system

Tell it plainly: this is for builders, engineers, and serious experimenters who respect the vehicle and understand risk.

Architecture (high level)

The stack follows a classic, layered model that actually makes sense in a car:

[ GM Vehicle Networks ]
        │
   VCX SE Pro
        │
   Khadas VIM3 (HMI + Compute)
        │
 ┌───────────────┬───────────────┐
 ESP32 Nodes   HDMI Dashboards   Comma Two / Pixhawk


Data flows up. Control flows down. Responsibility stays clear.

Getting Started (bare minimum)

Hardware required

1st-gen Chevy Volt

VCX SE Pro

Khadas VIM3

HDMI display

ESP32 dev board

Optional: Comma Two + Pixhawk

Basic bring-up

Connect VCX SE to the Volt’s diagnostic port

Bridge VCX SE to VIM3 via Ethernet

Boot VIM3 and launch HMI

Verify live CAN data streaming

Add ESP32 nodes as needed

No magic. Just wiring, configuration, and discipline.

License

This project is released under the MIT License. You are free to use, modify, and distribute — but you own the consequences of what you build.

Roadmap (what comes next)

Stable CAN data schema for Gen-1 Volt

Standardized HMI layouts

Plug-in module system for ESP32 nodes

Open documentation of key Volt messages

Reproducible test setups

Contributing

If you contribute, do it like a professional:

Document your work

Show your wiring

Explain your assumptions

Avoid black boxes

Pull requests without documentation will be closed.
