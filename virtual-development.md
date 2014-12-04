## Virtual development environment

The virtual guest is installed forward port xxx

### Installation

- Download and install latest [VirtualBox][]
- Download and install latest [Vagrant][]
- Clone GitHub repo:
    
    ```
    $ git clone https://github.com/rikardq/rimi.git
    $ cd rimi
    ```
- Import the vagrant box:
    
    ```
    $ vagrant box add precise64 http://files.vagrantup.com/precise64.box
    ```
- Start virtual development environment:
    
    ```
    $ vagrant up
    ```

- SSH to the virtual development environment:
    
    ```
    $ vagrant ssh
    ```
- You will find your project shared in `/vagrant` inside the virtual environment.  
    
    ```
    $ cd /vagrant
    ```

TODO link rimi to web2py server ... 

[Vagrant]: http://www.vagrantup.com/
[VirtualBox]: https://www.virtualbox.org/
