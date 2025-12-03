# Environment Setup
This is a guide to install WSL, integrate it in VSCode, and other things...

## 1. Install WSL

### Install command
  Open PowerShell in administrator mode, and write
```bash
wsl --install
```

### Set username and password
- This User Name and Password is specific to each separate Linux distribution that you install
- Please note that whilst entering the Password, nothing will appear on screen. This is called blind typing
- Once you create a User Name and Password, the account will be your default user for the distribution and automatically sign-in on launch
- This account will be considered the Linux administrator, with the ability to run sudo (Super User Do) administrative commands
- Each Linux distribution running on WSL has its own Linux user accounts and passwords. You will have to configure a Linux user account every time you add a distribution, reinstall, or reset
  
*To change or reset your password, open the Linux distribution and enter the command: `passwd`*
    
### Update and upgrade packages
```bash
sudo apt update && sudo apt upgrade
```

### File storage
To open your WSL project in Windows File Explorer, enter: `explorer.exe .`

*Be sure to add the period at the end of the command to open the current directory*

## 2. Set Up WSL in VSCode
Why?
- develop in a Linux-based environment
- use Linux-specific toolchains and utilities
- run and debug your Linux-based applications from the comfort of Windows
- use the VS Code built-in terminal to run your Linux distribution of choice

nice.

### Install VSCode
...

### Install extension pack
Install the [Remote Development extension pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)

### Update Linux Distribution
```bash
sudo apt-get update
sudo apt-get install wget ca-certificates
```

### Open a WSL project in Visual Studio Code
From the command-line: Open the distribution's command line and enter: `code .`

From VS Code: Use the shortcut: `Ctrl + Shift + P` in VS Code to bring up the command palette. If you then type `WSL` you will see a list of the options available

### Extensions inside of VS Code WSL
The WSL extension splits VS Code into a “client-server” architecture, with the client (the user interface) running on your Windows machine and the server (your code, Git, plugins, etc) running "remotely" in your WSL distribution.

When running the WSL extension, selecting the 'Extensions' tab will display a list of extensions split between your local machine and your WSL distribution.

<img width="586" height="320" alt="image" src="https://github.com/user-attachments/assets/5b5c01bb-5890-4942-a5ea-517a28572327" />

## 3. Git Setup
Git is the most commonly used version control system. With Git, you can track changes you make to files, so you have a record of what has been done, and have the ability to revert to earlier versions of the files if needed. Git also makes collaboration easier, allowing changes by multiple people to all be merged into one source

### Installing Git
```bash
sudo apt-get install git
```

### Git config file setup
```bash
git config --global user.email "youremail@domain.com"
git config --global user.name "Your Name"
```

### Commands to check and set up GCM for WSL
```bash
git --version; git credential-manager --version
```

### Additional configuration for Azure
```bash
git config --global credential.https://dev.azure.com.useHttpPath true
```

### Adding a Git Ignore file (Optional)
1. Open Git Bash.
2. Navigate to the location of your Git repository.
3. Create a .gitignore file for your repository.
   
[Some common .gitignore configurations](https://gist.github.com/octocat/9257657)

## 4. Docker Setup

## 5. Set up a database

## 6. Set up GPU acceleration for faster performance

## 7. Basic WSL commands

## 8. Mount an external drive or USB

## 9. Run Linux GUI apps

# Azure DevOps Integration: Agile Software Development
Think of Agile as a way of working where teams deliver value in small, frequent increments, continuously improving as they go

## The Agile Workflow

### 1. Sprint Planning (start of sprint)
The team decides:
- What work to bring into the next 1–2 week sprint
- How the work will be done
- Who will take what tasks

### 2. Daily Standup (every morning)
You answer three things:
- What you did yesterday
- What you’re doing today
- If anything is blocking you

*Tip: Keep answers short — 30 seconds is ideal*
