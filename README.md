# \# Volt Open Source Platform (VOSP)

# \*\*Repo:\*\* `VoltOpenSourcePlatform-project`

# 

# Open-source platform for 1st-gen Chevy Volt integrating VCX SE Pro, Khadas VIM3, HDMI dashboards, ESP32 edge nodes, and optional Pixhawk + Comma Two.

# 

# ---

# 

# \## Executive Summary

# This repository houses an open-source hardware–software integration platform for the 1st-generation Chevrolet Volt. The objective is simple and traditional: build a reliable, transparent, and serviceable digital backbone that sits alongside GM’s original systems — not replaces them — and gives engineers, researchers, and builders real visibility into how the car thinks, talks, and behaves.

# 

# This is not a toy dashboard. It is a modular instrumentation and data architecture that integrates professional-grade tools into a single, coherent stack.

# 

# ---

# 

# \## What This Platform Integrates

# The system is built around five core pillars:

# 

# \### 1) VCX SE Pro (DoIP/CAN Gateway)

# \- Enterprise-class vehicle interface  

# \- Secure access to GM networks  

# \- Bidirectional CAN and diagnostics capability  

# 

# \### 2) Khadas VIM3 (Android Automotive HMI Host)

# \- Runs the primary Human–Machine Interface (HMI)  

# \- Drives HDMI displays  

# \- Acts as the computing spine for visualization, logging, and control prototypes  

# 

# \### 3) HDMI Dashboards

# \- Custom digital cluster displays  

# \- Real-time vehicle telemetry  

# \- Configurable layouts for testing, validation, and demonstration  

# 

# \### 4) ESP32 Edge Nodes

# \- Low-level sensing and peripheral control  

# \- Local telemetry collection  

# \- Modular expansion for additional instrumentation  

# 

# \### 5) Pixhawk + Comma Two (Autonomy Research Stack) — Optional

# \- Experimental autonomy interface  

# \- High-rate sensor fusion and computer vision  

# \- Research pathway toward advanced driver assistance exploration  

# 

# ---

# 

# \## Scope — What This Is and Is Not

# 

# \### This platform IS:

# \- A research and development environment  

# \- A diagnostic and telemetry framework  

# \- A proving ground for Volt instrumentation  

# \- A transparent alternative to black-box OEM tools  

# 

# \### This platform is NOT:

# \- A production replacement for GM modules  

# \- A consumer plug-and-play product  

# \- A warranty-safe aftermarket device  

# \- A fully autonomous driving system  

# 

# Tell it plainly: this is for builders, engineers, and serious experimenters who respect the vehicle and understand risk.

# 

# ---

# 

# \## Architecture (High Level)

# The stack follows a classic, layered model that actually makes sense in a car:

# 



