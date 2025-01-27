Developer Guide
===============

Architecture Overview
---------------------

The framework is built with the following architecture:

...

Extending the Framework
-----------------------

To add a new model, follow these steps:

...

Building the Documentation
--------------------------

The project documentation is built using Sphinx, a powerful tool that generates HTML documentation from reStructuredText files. Follow these steps to build the documentation:

1. **Navigate to the `docs` directory:**

   From the project's root directory, switch to the `docs` folder where the Sphinx configuration is located:

   .. code-block:: bash

      cd docs

2. **Generate the API documentation:**

   If you are on Windows, we have made a script to easily clear the HTML tree, generate the code documentation and then create the HTML pages including the manually written content and the generated content.
      
   This is how to run the script on Windows:

   .. code-block:: bash

      .\update_docs.bat

   If you are on another operating system than Windows, you may adopt the script to your OS.

3. **How the script works:**

   Before generating the documentation, it's a good idea to clean any previous build artifacts to avoid conflicts:

   .. code-block:: bash

      make clean
   
   The script uses the `sphinx-apidoc` command to automatically generate reStructuredText files for your Python modules.

   To build the HTML documentation, run the following command to compile the documentation into HTML files:

   .. code-block:: bash

      make html

   The HTML files will be generated in the `build/html` directory.

Hosting the Documentation
-------------------------

Once the HTML documentation is built, it needs to be hosted on a web server so that team members can access it through their browsers.

1. **Locate the built documentation:**

   The HTML files are located in the `build/html` directory under the `docs` folder.

2. **Move the documentation to the web server:**

   Copy the contents of the `build/html` directory to a web server directory. The method depends on your hosting setup. For example:
   - If you use an FTP server, upload the files via an FTP client.
   - If you use a cloud platform, sync the files using their command-line tools (e.g., `aws s3 sync`, `gsutil cp`, etc.).

3. **Access the documentation in your browser:**

   Once hosted, the documentation will be accessible via a URL like `http://yourserver.com/docs`. Share this URL with your team so they can access the latest version of the documentation.

By following these steps, you ensure that the project documentation is up-to-date and accessible to everyone involved.
