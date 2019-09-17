# TUG-Server
This implements the core functionality for the automatic evaluation of TUG-Tests (Timed Up and Go test, [see here](https://de.wikipedia.org/wiki/Timed_up_and_go_test)).

This implementation uses machine learning for the classification of the different phases of the test (stand-up, walk, rotate, sit down). The model needs to be trained before usage. A pre-trained model can be derived from the LabeledData. The server expects a live data-stream on a rabbit-mq server, which is produced by [the corresponding android app](https://github.com/cjmoeller/tug-app).

A short overview (in german) of the project is provided in the [overview.pdf](/overview.pdf).

Contributors: @hwiards, @cjmoeller, Christian Steger
