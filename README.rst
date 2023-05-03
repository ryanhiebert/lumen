Installing on a Raspberry Pi
============================

Install a vanilla headless Raspberry Pi OS.
If you're using a smaller SD card like I am,
be sure to install the "Lite" version.

I used the Raspberry Pi Imager app for Mac.
Be sure to check on the settings before you image the disk.
You will want to make sure you have SSH turned on,
and that you have configured a user account for SSH.

Then SSH into the fresh OS, and follow these instructions.


Install main packages
---------------------

You should install a couple packages::

    sudo apt install git python3-venv

If you need to be space conscious, run::

    sudo apt clean


Configuring the shared location
-------------------------------

Because I want to have this be a shared folder,
I made a folder called `lumen` at the root.
I made a `lumen` group, added myself to it,
and set the folder's group owner to `lumen`.
I also set the group sticky and write bits on the folder.

::

    sudo mkdir /lumen
    sudo addgroup lumen
    sudo adduser ryan lumen
    sudo chown :lumen /lumen
    sudo chmod g+rws /lumen


That's almost enough,
but I also needed to set the default umask to 002 instead of 022,
so that new files created in that folder would be group writable.

I did that by adding the following line to the end of `/etc/pam.d/common-session::

    session optional pam_umask.so umask=002

The log out and log back in so that it knows you're part of the group.

Once that was done I can now clone the repository into a subdirectory of `/lumen`.

    cd /lumen
    git clone https://github.com/ryanhiebert/lumen.git \
        --config core.sharedRepository=group --depth 1


Setup Lumen
===========

Still at the `/lumen` directory, we want to create a new venv,
install lumen into it, add the systemd configuration,
and get systemd to automatically start lumen on boot.

Create the venv by running::

    python3 -m venv venv

Then install the lumen package::

    source venv/bin/activate
    pip install ./lumen
    deactivate

Create the systemd service file.
Use the `lumen.service` file in the repository as a guide.
Be sure to edit it as appropriate,
paying particular attention to the configuration.

::

    sudo cp lumen/lumen.service /etc/systemd/system/

Then enable lumen to start on boot::

    sudo systemctl daemon-reload
    sudo systemctl start lumen
    sudo systemctl enable lumen

Then go to the IP address in your browser.
If things don't seem to be loading,
check out the logs::

    sudo tail -f /var/log/syslog


Static IP Configuration
=======================

You may wish to enable a Static IP address.
To set up the static IP as a fallback to normal DHCP,
add the following configuration
to the end of the ``/etc/dhcpcd.conf``.

For me, this was::

    # fallback to static profile on eth0
    #interface eth0
    #fallback static_eth0

    interface eth0

    static ip_address=192.168.10.38
    static routers=192.168.10.1
    static domain_name_servers=192.168.10.1
