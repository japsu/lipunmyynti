from django.db import models
import md5

# Create your models here.
class Payment(models.Model):
    test = models.IntegerField(blank=True, null=True)
    VERSION = models.CharField(max_length=4)
    STAMP = models.CharField(max_length=20)
    REFERENCE = models.CharField(max_length=20)
    PAYMENT = models.CharField(max_length=20)
    STATUS = models.IntegerField()
    ALGORITHM = models.IntegerField()
    MAC = models.CharField(max_length=32)

    def check_mac(self):
        password = "SAIPPUAKAUPPIAS"
    	_mac = md5.new()
    	_mac.update(password)
        _mac.update("&")
    	_mac.update(self.VERSION)
        _mac.update("&")
    	_mac.update(self.STAMP)
        _mac.update("&")
    	_mac.update(self.REFERENCE)
        _mac.update("&")
    	_mac.update(self.PAYMENT)
        _mac.update("&")
    	_mac.update(str(self.STATUS))
        _mac.update("&")
    	_mac.update(str(self.ALGORITHM))
    	if self.MAC != _mac.hexdigest().upper():
    		raise RuntimeError(self.MAC+' '+str(_mac.hexdigest()).upper())    