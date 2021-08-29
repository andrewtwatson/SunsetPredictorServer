from django.db import models

class Error(models.Model):

    # date of the error
    date = models.DateTimeField('Date and Time of Recording')
    # category of error
    type = models.CharField(max_length=100)
    # info of the error
    info = models.TextField()

    def __str__(self) -> str:
        """
        Override string display info about the error
        """
        string = "date: " + str(self.date) + ", type: " + str(self.type) + ", info: " + str(self.info)
        return string