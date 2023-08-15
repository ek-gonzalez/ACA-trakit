from django.db import models

# Create your models here.

class Suser(models.Model):
    suserid = models.AutoField(primary_key=True)
    id = models.CharField(max_length=11, blank=False, null=False)
    inHuddle = models.BooleanField(blank=False, null=False, default=False)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"#{self.id}"



class Pair(models.Model):
    member1 = models.ForeignKey(Suser, on_delete=models.CASCADE, related_name="pm1")
    member2 = models.ForeignKey(Suser, on_delete=models.CASCADE, related_name="pm2")

    def __str__(self):
        return f"#{self.member1.id} and #{self.member2.id}"



class Project(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    members_pair = models.ForeignKey(Pair, on_delete=models.CASCADE)

    def __str__(self):
        return f"Project {self.name}: {self.members_pair}"




class Task(models.Model):
    name = models.CharField(max_length=80, blank=False, null=False)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"Task #{self.id}: {self.name}"

