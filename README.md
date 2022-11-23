Arteria bclconvert
=================

A self contained (Tornado) REST service for running Illuminas bcl-convert.

Trying it out
-------------
The easiest way to try out `arteria-bclconvert` is to run it in the provided Vagrant box. Note that you will need to download Illumina software bcl-convert manually since Illumina requires that you register before donwloading. Download the [zip](https://webdata.illumina.com/downloads/software/bcl-convert/bcl-convert-4.0.3-2.el7.x86_64.rpm) file containing the rpm. Save in at docker-images/bcl2fastq-service/local_files

    # get the vagrant environment running
    # Please note that starting this vm requires 4 GB or RAM (since bcl2fastq requires alot of memory to run)
    vagrant up

    # ssh into it
    vagrant ssh

    # move into the vagrant working directory
    cd /vagrant

    # create a virtual environment and activate it
    virtualenv-3 venv && source venv/bin/activate

    # update pip (unfortunately the installed verison is to old)
    pip install --upgrade pip    

    # install bclconvert (with -e for "editable" to make development easier)
    cd arteria-bclconvert && pip install -r requirements/dev .

Now you can try running it:

     bclconvert-ws --config config/ --port 8888

And then you can find a simple api documentation by opening up an additional terminal by running going to:

    curl http://localhost:8888/api | python -m json.tool

To try things out a bit more, you need to setup a path to watch and place some runfolders there, e.g.

    # Create the following folders under the /vagrant directory (or anywhere you like, but then
    # you need to make the corresponding changes in the `config/app.config`).
    mkdir ./bclconvert_logs ./runfolder_output

    # Clone a directory with test data
    git clone https://github.com/roryk/tiny-test-data.git

    # Start the service again
    bclconvert-ws --config config/ --port 8888

    # And now you can kick of running bcl2fastq on the small runfolder by:
    # Update to bcl-convert example
    curl -X POST --data '{"additional_args": "--ignore-missing-bcls --ignore-missing-filter --ignore-missing-positions --ignore-missing-controls"}' http://localhost:8888/api/1.0/start/flowcell

    # You can poll its status on the returned link, or you can poll
    curl http://localhost:8888/api/1.0/status/
