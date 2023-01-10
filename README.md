Arteria bclconvert
=================

A self contained (Tornado) REST service for running Illuminas bcl-convert.

Trying it out
-------------
The easiest way to try out `arteria-bclconvert` is to run it in the provided docker-compose file. There is both a dummy implementation and a real service, note that you will need to download Illumina software bcl-convert manually since Illumina requires that you register before donwloading. Download the [zip](https://webdata.illumina.com/downloads/software/bcl-convert/bcl-convert-4.0.3-2.el7.x86_64.rpm) file containing the rpm. Save in at docker-images/bcl2fastq-service/local_files

    # Run dummy implementation
    docker-compose -f docker-compose-test.yaml up

And then you can find a simple api documentation by opening up an additional terminal by running going to:

    curl http://localhost:10900/api | python3 -m json.tool

    # Start conversion of dummy daya example
    curl -X POST --data '{"additional_args": ""}' http://localhost:10900/api/1.0/start/runfolder1

    # You can poll its status on the returned link, or you can poll
    ## all entries
    curl http://localhost:8888/api/1.0/status/
    ## specifc entry
    curl http://localhost:8888/api/1.0/status/1
