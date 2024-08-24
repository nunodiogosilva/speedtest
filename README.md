# Speedtest Service
## Getting Started
Speedtest Service is a Python-based project that focuses on setting up a Speedtest service on a Raspberry Pi, using tools like Prometheus, Grafana, and GitHub Actions for monitoring and automation. The repository provides a step-by-step guide on installation and setup, including creating a virtual environment, installing necessary packages, and configuring Prometheus and Grafana.

## Ookla Speedtest
TODO (Add Ookla Speedtest info)

## Raspberry Pi
A Raspberry Pi is a small, affordable, single-board computer. Developed by the [Raspberry Pi Foundation](https://www.raspberrypi.org/), it has gained widespread popularity for its versatility and low cost. A Raspberry Pi is a popular choice for running Prometheus and Grafana projects, especially for small-scale or home-based monitoring setups. In order to configure our Raspberry Pi, we may refer to [Getting started](https://www.raspberrypi.com/documentation/computers/getting-started.html#getting-started-with-your-raspberry-pi) Raspberry Pi official documentation. In Speedtest Service case we've used a Raspberry Pi 3 Model B with Raspberry Pi OS Lite (64-bit) operating system and a SD card with 32GB of storage.

## Prerequisites
TODO (Add prerequisites info)

  ### 1. Clone GitHub Repository
  * Firstly let's ensure that your packages are up to date and then install Git.
  ```bash
  sudo apt-get update
  sudo apt-get install git
  ```

  * (Optional) To verify that Git is installed, we may run the command below.
  ```bash
  git --version
  ```

  * Create */scripts* directory.
  ```bash
  sudo mkdir /scripts && cd /scripts
  ```

  * Clone [Speedtest Service](https://github.com/nunodiogosilva/speedtest.git) GitHub repository into */scripts* directory.
  ```bash
  sudo git clone https://github.com/nunodiogosilva/speedtest.git && cd speedtest
  ```

  * Change the ownership of */scripts* directory to your user, you may use the command below. Make sure to replace *USERNAME* with your username.
  ```bash
  sudo chown -R <USERNAME>:root /scripts
  ```

  ### 2. Create Virtual Environment
  Python virutal environments isolate dependencies for projects, allowing different projects to use different packages and versions without conflicts. They ensure clean, independent setups. You may refer to [Python Packaging](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) official documentation for additional information about Python virtual environments.

  * To create a virtual environment, run the command below in */scripts/speedtest* directory. This will create a new virtual environment in a local folder named *.venv*.
  ```bash
  python3.11 -m venv .venv
  ```

  * Before you can start installing or using packages in your virtual environment you'll need to activate it in */scripts/speedtest* directory. Activating a virtual environment will put the virtual environment specific Python and pip executables into your terminal.
  ```bash
  source .venv/bin/activate
  ```

  * (Optional) If you want to switch projects or leave your virtual environment, you may deactivate it using the command below in */scripts/speedtest* directory.
  ```bash
  deactivate
  ```

  ### 3. Python PIP Requirements
  * Run the command below in */scripts/speedtest* directory where *requirements.txt* file is located. This command will read *requirements.txt* file and install all the specified packages and their dependencies.
  ```bash
  pip3.11 install -r requirements.txt
  ```

  * (Optional) Alternatively, if you've installed a new Python package that it's not in *requirements.txt* file, you may use the command below in */scripts/speedtest* directory to list all the packages installed and their versions. You then redirect the output to *requirements.txt* file.
  ```bash
  pip3.11 freeze > requirements.txt
  ```

  * (Optional) If you want to start fresh but you don't want to delete the virtual environment that you've created, you may uninstall all Python packages running the command below in */scripts/speedtest* directory.
  ```bash
  pip3.11 freeze | xargs pip3.11 uninstall -y
  ```

  * (Optional) To get the most up to date packages versions and upgrade them automatically we may use *pip-review* package which lists available updates and it can also automatically or interactively install available updates. Run the command below in */scripts/speedtest* directory. You may refer to [PyPI](https://pypi.org/project/pip-review/) official documentation for additional information about *pip-review* Python package.
  ```bash
  pip-review --interactive
  ```

  ### 4. Prometheus
  Prometheus is an open-source monitoring and alerting toolkit designed for reliability and scalability. Prometheus stores all metrics data as time series and will be used has a datasource. **If you're using a different operating system please refer to [Getting Started](https://prometheus.io/docs/prometheus/latest/getting_started/) and to [Download](https://prometheus.io/download/) Prometheus official documentation to find the installation and configuration steps for your operating system.**
  
  * In order to install Prometheus in our Raspberry Pi, we may use the commands below.
  ```bash
  sudo apt-get install prometheus
  ```

  * Prometheus should start automatically after installation. To ensure it starts on boot, we need to enable it.
  ```bash
  sudo systemctl enable prometheus
  sudo systemctl start prometheus
  ```

  * (Optional) To verify that Prometheus is running, we may run the command below.
  ```bash
  sudo systemctl status prometheus
  ```

  * You can access the Prometheus web UI at [localhost:9090](http://localhost:9090).

  ### 5. Grafana
  Grafana is an open-source platform for monitoring and observability, which allows users to visualize, analyze, and understand metrics, logs, and traces collected from various sources in real-time. Grafana will be used to visualize Prometheus datasource metrics. **If you're using a different operating system please refer to [Install Grafana](https://grafana.com/docs/grafana/latest/setup-grafana/installation/) official documentation to find the installation and configuration steps for your operating system.**
  
  * In order to install Grafana in our Raspberry Pi, we may use the commands below.
  ```bash
  sudo apt-get install -y apt-transport-https software-properties-common wget
  ```

  * Import GPG key.
  ```bash
  sudo mkdir -p /etc/apt/keyrings/
  wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
  ```

  * Add a repository for stable releases.
  ```bash
  echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
  ```

  * Update the list of available packages.
  ```bash
  sudo apt-get update
  ```

  * Install Grafana.
  ```bash
  sudo apt-get install grafana
  ```

  * After installation, you need to start Grafana. To ensure it starts on boot, we need to enable it.
  ```bash
  sudo systemctl enable grafana-server
  sudo systemctl start grafana-server
  ```

  * (Optional) To verify that Grafana is running, we may run the command below.
  ```bash
  sudo systemctl status grafana-server
  ```

  * You can access the Grafana web UI at [localhost:3000](http://localhost:3000).

  ### 6. Speedtest Service Setup
  * In order to setup Speedtest Service on your Raspberry Pi, you may set it up automatically or manually. To do it automatically you may use the command below in */scripts/speedtest* directory.
  ```bash
  python3.11 -m app.setup
  ```

  * (Optional) If you want to setup Speedtest Service manually, you may follow the steps below.
    #### 1. Prometheus
    * Edit Prometheus configuration file to include the metrics generated by Speedtest Service.
    ```bash
    sudo rm /etc/prometheus/prometheus.yml
    sudo touch /etc/prometheus/prometheus.yml
    sudo nano /etc/prometheus/prometheus.yml
    ```

    * Copy and paste the following Prometheus configuration file content.
    ```yml
    # Global configuration
    global:
      scrape_interval: 15s # How often to scrape metrics (default is 1m)
      evaluation_interval: 15s # How often to evaluate rules (default is 1m)

    # A scrape configuration containing endpoints to scrape.
    scrape_configs:
      - job_name: 'prometheus'
        static_configs:
          - targets: ['localhost:9090']

      - job_name: 'node'
        static_configs:
          - targets: ['localhost:9100']

      - job_name: 'metrics'
        static_configs:
          - targets: ['localhost:8000']
    ```

    * Restart Prometheus in order to add the configurations.
    ```bash
    sudo systemctl restart prometheus
    ```

    #### 2. Grafana
    * TODO (Add Service Account Token) 
    * TODO (Add datasource)
    * TODO (Add dashboard)

    #### 3. Systemd Service
    A Systemd service is a system unit managed by Systemd init system in Linux. It allows to define and control the behavior of a application, such as starting it at boot, stopping it, restarting it and checking it status. You may refer to [Systemd](https://systemd.io/) official website for additional information.

    * Let's now create a new Systemd service for Speedtest Service using the commands below.
    ```bash
    sudo touch /etc/systemd/system/speedtest.service
    sudo nano /etc/systemd/system/speedtest.service
    ```

    * Copy and paste the following Systemd configuration file content.
    ```ini
    [Unit]
    Description=Speedtest Service
    After=network.target

    [Service]
    EnvironmentFile=/scripts/speedtest/.env
    WorkingDirectory=/scripts/speedtest
    ExecStart=/usr/bin/sh -c "cd /scripts/speedtest && .venv/bin/python3.11 -m app.run"
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

    * After creating a Systemd service for Speedtest Service, you'll need to reload Systemd files and start Speedtest Service. To ensure it starts on boot, we also need to enable it.
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable speedtest.service
    sudo systemctl start speedtest.service
    ```

    * To verify that Speedtest Service is running, we may run the command below.
    ```bash
    sudo systemctl status speedtest.service
    ```

  ### 7. (Optional) GitHub Actions
  GitHub Actions is a powerful automation platform integrated into GitHub that allows you to create, manage, and execute custom workflows directly within your GitHub repositories. It is most commonly used for continuous integration (CI) and continuous delivery (CD), enabling developers to automatically build, test, and deploy their code whenever changes are made.

  * To add a self-hosted runner, go to your GitHub repository or organization settings. Select Settings > Actions > Runners > Add Runner. Follow the instructions to download and configure the runner on your system. When installing your self-hosted runner be sure to **leave name of the runner group leave as *default***, that the **name of runner will be *speedtest***, to **leave runner labels as *default*** and that the **name of the work folder will be *speedtest***. **If you're using a different operating system please refer to [Add self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/adding-self-hosted-runners) GitHub Actions official documentation to find the installation and configuration steps for your operating system.**

  * In order to configure your self-hosted runner application to be a service and ensure that it starts on boot, we need to stop the self-hosted runner application if it is currently running. **If you're using a different operating system please refer to [Run the runner app as a service](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service) GitHub Actions official documentation to find the installation and configuration steps for your operating system.**

  * In order to install a self-hosted runner as a service in our Raspberry Pi, we may use the commands below.
  ```bash
  sudo ./svc.sh install
  ```

  * Start self-hosted runner service.
  ```bash
  sudo ./svc.sh start
  ```

  * (Optional) To verify that the self-hosted runner service is running, we may run the command below.
  ```bash
  sudo ./svc.sh status
  ```

## Speedtest Service CI/CD Flowchart
![speedtest_cicd_flowchart](assets/images/speedtest_cicd_flowchart.png)

## Tools
|                                                                                              | Name                                                                   | Purpose          |
|----------------------------------------------------------------------------------------------|------------------------------------------------------------------------|------------------|
| <img src="assets/images/vscode.png" alt="vscode" width="50" height="auto">                   | [Visual Studio Code](https://code.visualstudio.com/)                   | Code Editor      |
| <img src="assets/images/git.png" alt="git" width="50" height="auto">                         | [Git](https://git-scm.com/)                                            | Version Control  |
| <img src="assets/images/github.png" alt="github" width="50" height="auto">                   | [GitHub](https://github.com/)                                          | Code Repository  |
| <img src="assets/images/github_actions.png" alt="github_actions" width="50" height="auto">   | [GitHub Actions](https://github.com/features/actions)                  | CI/CD            |
| <img src="assets/images/raspberry_pi.png" alt="raspberry_pi" width="50" height="auto">       | [Raspberry Pi OS Lite (64-bit)](https://www.raspberrypi.com/software/) | Operating System |
| <img src="assets/images/systemd.png" alt="systemd" width="80" height="auto">                 | [Systemd](https://systemd.io/)                                         | Service          |
| <img src="assets/images/python.png" alt="python" width="50" height="auto">                   | [Python (3.11)](https://www.python.org/)                               | Scripting        |
| <img src="assets/images/ookla_speedtest.png" alt="ookla_speedtest" width="50" height="auto"> | [Ookla Speedtest](https://www.speedtest.net/)                          | Benchmarking     |
| <img src="assets/images/prometheus.png" alt="prometheus" width="50" height="auto">           | [Prometheus](https://prometheus.io/)                                   | Collect Metrics  |
| <img src="assets/images/grafana.png" alt="grafana" width="50" height="auto">                 | [Grafana](https://grafana.com/)                                        | Analyze Metrics  |

## Supported OS
|                                                                              | Name    |
|------------------------------------------------------------------------------|---------|
| <img src="assets/images/linux.png" alt="linux" width="50" height="auto">     | Linux   |
| <img src="assets/images/macos.png" alt="macos" width="50" height="auto">     | macOS   |
<!-- | <img src="assets/images/windows.png" alt="windows" width="50" height="auto"> | Windows | -->

## Authors & Maintainers
| Name       | LinkedIn                                                                      | Role   |
|------------|-------------------------------------------------------------------------------|--------|
| Nuno Silva | [in/nunodiogosilva](https://www.linkedin.com/in/nunodiogosilva/) | Author |

