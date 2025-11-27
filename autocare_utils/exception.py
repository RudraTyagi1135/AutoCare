# basic imports
import sys   # sys is used here to capture detailed exception information (stack trace, etc.)


# internal imports (importing the logger you defined earlier in logging/logger.py)
from  autocare_utils.logging import logging


# custom exception class for handling project-specific errors
class AutoCareException(Exception):
    """
    A custom exception class that extends Python's built-in Exception.
    Purpose:
    - Provide detailed error trace (filename, line number, message)
    - Centralized exception handling across the project
    """

    def __init__(self, error_message, error_details):
        """
        Constructor for custom exception.
        :param error_message: The actual error message that occurred.
        :param error_details: sys module object to capture traceback info.
        """
        self.error_message = error_message  # store the error message

        # error_details.exc_info() → gives tuple (type, value, traceback)
        # traceback object helps to locate where exactly the error occurred
        _, _, exc_tb = error_details.exc_info()

        if exc_tb is not None:
            self.lineno = exc_tb.tb_lineno
            self.file_name = exc_tb.tb_frame.f_code.co_filename
        else:
            self.lineno = "N/A"
            self.file_name = "N/A"

            
        # extract line number from traceback object
        self.lineno = exc_tb.tb_lineno

        # extract file name where exception occurred
        self.file_name = exc_tb.tb_frame.f_code.co_filename

    def __str__(self):
        """
        String representation of the exception.
        This is what will be printed if the exception is raised.
        """
        return (
            "Error occurred in python script name [{0}] "
            "line number [{1}] "
            "error message [{2}]"
        ).format(self.file_name, self.lineno, str(self.error_message))
