from django.db import models

from account.models import CustomUser


class Room(models.Model):
    number = models.CharField(max_length=5, blank=True, null=True)
    image_1 = models.ImageField(upload_to='rooms/images')
    image_2 = models.ImageField(upload_to='rooms/images')
    image_3 = models.ImageField(upload_to='rooms/images')
    image_4 = models.ImageField(upload_to='rooms/images')
    image_5 = models.ImageField(upload_to='rooms/images')
    beds = models.IntegerField()
    price_per_day = models.PositiveSmallIntegerField()
    has_discount = models.BooleanField(default=False, blank=True, null=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hsd_discount_implemented = models.BooleanField(default=False)

    is_reserved = models.BooleanField(default=False)
    reserved_by = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    days_to_stay = models.PositiveSmallIntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    final_price = models.PositiveSmallIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.has_discount and self.hsd_discount_implemented is False:
            self.price_per_day = self.price_per_day - (self.discount_percent / 100 * self.price_per_day)
            self.hsd_discount_implemented = True

        super(Room, self).save(*args, **kwargs)

    def __str__(self):
        return self.number


class UserReservationHistory(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    days = models.PositiveSmallIntegerField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class RoomHistory(models.Model):
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    days_to_stay = models.PositiveSmallIntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    has_discount = models.BooleanField(default=False, blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    final_price = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.room.number
