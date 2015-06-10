import re
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from django_monitor.conf import (
    PENDING_STATUS, CHALLENGED_STATUS, APPROVED_STATUS
)
from django_monitor.models import MonitorEntry
from django_monitor.tests.test_app.models import (
    Author, Book, EBook, Supplement, Publisher, Reader
)

def get_perm(Model, perm):
    """Return the permission object, for the Model"""
    ct = ContentType.objects.get_for_model(Model)
    return Permission.objects.get(content_type = ct, codename = perm)

def moderate_perm_exists(Model):
    """ Returns if moderate permission exists for the given model or not."""
    ct = ContentType.objects.get_for_model(Model)
    return Permission.objects.filter(
        content_type = ct,
        codename = 'moderate_%s' % Model._meta.object_name.lower()
    ).exists()

class ModPermTest(TestCase):
    """Make sure that moderate permissions are created for required models."""

    def test_perms_for_author(self):
        """Testing if moderate_perm exists for Author"""
        self.assertEquals(moderate_perm_exists(Author), True)

    def test_perms_for_book(self):
        """Testing if moderate_ perm exists for Book"""
        self.assertEquals(moderate_perm_exists(Book), True)

    def test_perms_for_supplement(self):
        """Testing if moderate_ perm exists for Supplement"""
        self.assertEquals(moderate_perm_exists(Supplement), True)

    def test_perms_for_publisher(self):
        """Testing if moderate_ perm exists for Publisher"""
        self.assertEquals(moderate_perm_exists(Publisher), False)

class ModTest(TestCase):
    """Testing Moderation facility"""
    fixtures = ['test_monitor.json']

    def get_csrf_token(self, url):
        """Scrape CSRF token"""
        response = self.client.get(url, follow = True)
        csrf_regex = r'csrfmiddlewaretoken\'\s+value=\'([^\']+)\''
        return re.search(csrf_regex, response.content).groups()[0]
    
    def setUp(self):
        """Two users, adder & moderator."""
        # Permissions
        add_auth_perm = get_perm(Author, 'add_author')
        ch_auth_perm = get_perm(Author, 'change_author')
        mod_auth_perm = get_perm(Author, 'moderate_author')
        add_bk_perm = get_perm(Book, 'add_book')
        ch_bk_perm = get_perm(Book, 'change_book')
        mod_bk_perm = get_perm(Book, 'moderate_book')
        add_ebk_perm = get_perm(EBook, 'add_ebook')
        ch_ebk_perm = get_perm(EBook, 'change_ebook')
        mod_ebk_perm = get_perm(EBook, 'moderate_ebook')
        add_sup_perm = get_perm(Supplement, 'add_supplement')
        mod_sup_perm = get_perm(Supplement, 'moderate_supplement')
        ch_reader_perm = get_perm(Reader, 'change_reader')
        ch_me_perm = get_perm(MonitorEntry, 'change_monitorentry')

        self.adder = User.objects.create_user(
            username = 'adder', email = 'adder@monitor.com',
            password = 'adder'
        )
        self.adder.user_permissions = [
            add_auth_perm, add_bk_perm, add_ebk_perm, add_sup_perm,
            ch_auth_perm, ch_reader_perm, ch_me_perm
        ]
        self.adder.is_staff = True
        self.adder.save()
        self.moderator = User.objects.create_user(
            username = 'moder', email = 'moder@monitor.com',
            password = 'moder'
        )
        self.moderator.user_permissions = [
            add_auth_perm, add_bk_perm, add_ebk_perm, add_sup_perm,
            mod_auth_perm, mod_bk_perm, mod_ebk_perm, mod_sup_perm,
            ch_auth_perm, ch_bk_perm, ch_ebk_perm, ch_reader_perm, ch_me_perm
        ]
        self.moderator.is_staff = True
        self.moderator.save()

    def tearDown(self):
        self.adder.delete()
        self.moderator.delete()

    def test_1_check_additional_fields(self):
        """
        monitor puts some additional attrs to each moderated class.
        Let's check for their existence.
        """
        import django_monitor
        qd_book = django_monitor.model_from_queue(Book)
        monitor_name = qd_book['monitor_name']
        status_name = qd_book['status_name']
        self.assertEquals(hasattr(Book, monitor_name), True) 
        self.assertEquals(hasattr(Book, 'monitor_status'), True)
        self.assertEquals(hasattr(Book, status_name), True)
        self.assertEquals(hasattr(Book, 'get_monitor_status_display'), True)
        self.assertEquals(hasattr(Book, 'moderate'), True)
        self.assertEquals(hasattr(Book, 'approve'), True)
        self.assertEquals(hasattr(Book, 'challenge'), True)
        self.assertEquals(hasattr(Book, 'reset_to_pending'), True)
        self.assertEquals(hasattr(Book, 'is_approved'), True)
        self.assertEquals(hasattr(Book, 'is_challenged'), True)
        self.assertEquals(hasattr(Book, 'is_pending'), True)
        # monitor has changed the default manager, ``objects`` too.
        self.assertEquals(
            str(Book.objects)[:34], '<django_monitor.util.CustomManager'
        )

    def test_2_moderation(self):
        """ 
        Adder has permission to add only. All of his objects are in Pending.
        Moderator has permissions to add & moderate also. All objects he 
        creates are auto-approved.
        """
        # adder logs in. 
        logged_in = self.client.login(username = 'adder', password = 'adder')
        self.assertEquals(logged_in, True)
        # Make sure that no objects are there 
        self.assertEquals(Author.objects.count(), 0) 
        self.assertEquals(Book.objects.count(), 0)
        self.assertEquals(Supplement.objects.count(), 0)
        # Adding 2 Author instances...
        url = '/admin/test_app/author/add/'
        # Author 1
        data = {'age': 34, 'name': "Adrian Holovaty"}
        response = self.client.post(url, data, follow = True)
        # Author 2
        data = {'age': 35, 'name': 'Jacob kaplan-Moss'}
        response = self.client.post(url, data, follow = True)
        self.assertEquals(response.status_code, 200)
        # 2 Author instances added. Both are in pending (IP)
        self.assertEquals(Author.objects.count(), 2)
        self.assertEquals(Author.objects.get(pk = 1).is_pending, True)
        self.assertEquals(Author.objects.get(pk = 2).is_pending, True)
        # Adding 1 book instance with 2 supplements...
        url = '/admin/test_app/book/add/'
        data = {
            'publisher': 1, 'isbn': '159059725', 'name': 'Definitive', 
            'authors': [1, 2], 'pages': 447,
            'supplements-TOTAL_FORMS': 2, 'supplements-INITIAL_FORMS': 0,
            'supplements-0-serial_num': 1, 'supplements-1-serial_num': 2,
        }
        response = self.client.post(url, data, follow = True)
        self.assertEquals(response.status_code, 200)
        # 1 Book instance added. In pending (IP)
        self.assertEquals(Book.objects.count(), 1)
        self.assertEquals(Book.objects.get(pk = 1).is_pending, True)
        # 2 Supplement instances added. In Pending (IP)
        self.assertEquals(Supplement.objects.count(), 2)
        self.assertEquals(Supplement.objects.get(pk = 1).is_pending, True)
        self.assertEquals(Supplement.objects.get(pk = 2).is_pending, True)

        # Adder logs out
        self.client.logout()
    
        # moderator logs in. 
        logged_in = self.client.login(username = 'moder', password = 'moder')
        self.assertEquals(logged_in, True)
        # Adding one more author instance...
        url = '/admin/test_app/author/add/'
        # Author 3
        data = {'age': 46, 'name': "Stuart Russel"}
        response = self.client.post(url, data, follow = True)
        # Author 3 added. Auto-Approved (AP)
        self.assertEquals(Author.objects.count(), 3)
        self.assertEquals(Author.objects.get(pk = 3).is_approved, True)
        # Approve Author 1 (created by adder)
        url = '/admin/test_app/author/'
        data = {'action': 'approve_selected', 'index': 0, '_selected_action': 1}
        response = self.client.post(url, data, follow = True)
        self.assertEquals(Author.objects.get(pk = 1).is_approved, True)
        # Challenge Author 2 (created by adder)
        data = {'action': 'challenge_selected', 'index': 0, '_selected_action': 2}
        response = self.client.post(url, data, follow = True)
        self.assertEquals(Author.objects.get(pk = 2).is_approved, False)
        self.assertEquals(Author.objects.get(pk = 2).is_challenged, True)
        # Approve Book 1 (created by adder). Supplements also get approved.
        url = '/admin/test_app/book/'
        data = {'action': 'approve_selected', 'index': 0, '_selected_action': 1}
        response = self.client.post(url, data, follow = True)
        self.assertEquals(Book.objects.get(pk = 1).is_approved, True)
        self.assertEquals(Supplement.objects.get(pk = 1).is_approved, True)
        self.assertEquals(Supplement.objects.get(pk = 2).is_approved, True)

        # moderator logs out
        self.client.logout()
        # adder logs in again
        logged_in = self.client.login(username = 'adder', password = 'adder')
        self.assertEquals(logged_in, True)

        # Edit the challenged Author, author 2.
        self.failUnlessEqual(Author.objects.get(pk = 2).age, 35)
        url = '/admin/test_app/author/2/'
        data = {'id': 2, 'age': 53, 'name': 'Stuart Russel'}
        response = self.client.post(url, data)
        self.assertRedirects(
            response, '/admin/test_app/author/', target_status_code = 200
        )
        self.failUnlessEqual(Author.objects.get(pk = 2).age, 53)
        # Reset Author 2 back to pending
        url = '/admin/test_app/author/'
        data = {'action': 'reset_to_pending', 'index': 0, '_selected_action': 2}
        response = self.client.post(url, data, follow = True)
        self.failUnlessEqual(Author.objects.get(pk = 2).is_pending, True)

    def test_3_moderate_parents_from_shell(self):
        """
        Moderate instance of a sub-class model. Parents also must be moderated.
        Run from the shell.
        """
        pub1 = Publisher.objects.create(
            name = 'test_pub', num_awards = 3
        )
        auth1 = Author.objects.create(
           name = 'test_auth', age = 34
        )
        eb1 = EBook.objects.create(
            isbn = '123456789', name = 'test_ebook', 
            pages = 300, publisher = pub1
        )
        eb1.authors = [auth1]
        eb1.save()
        # The parent instance book_ptr is available
        book_ptr = getattr(eb1, 'book_ptr', None)
        self.assertEquals(book_ptr is None, False)
        # Both are in pending now
        self.assertEquals(eb1.is_pending, True)
        self.assertEquals(book_ptr.is_pending, True)
        # Approve eb1.
        eb1.approve()
        # Load again from db. Else, cached value may be used.
        eb1 = EBook.objects.get(pk = 1)
        self.assertEquals(eb1.is_approved, True)
        self.assertEquals(eb1.book_ptr.is_approved, True)

    def test_4_moderate_parents_from_browser(self):
        """
        Moderate instance of a sub-class model. Parents also must be monitored.
        User makes requests from a browser.
        """
        # The adder starts it as usual...
        logged_in = self.client.login(username = 'adder', password = 'adder')
        self.assertEquals(logged_in, True)

        pub1 = Publisher.objects.create(
            name = 'test_pub', num_awards = 3
        )
        auth1 = Author.objects.create(
           name = 'test_auth', age = 34
        )
        url = '/admin/test_app/ebook/add/'
        data = {
            'publisher': 1, 'isbn': '159059725', 'name': 'Definitive', 
            'authors': [1,], 'pages': 447,
            'supplements-TOTAL_FORMS': 0, 'supplements-INITIAL_FORMS': 0,
        }
        response = self.client.post(url, data, follow = True)
        self.assertEquals(response.status_code, 200)
        # 1 EBook instance added. In pending (IP)
        self.assertEquals(EBook.objects.count(), 1)
        self.assertEquals(EBook.objects.get(pk = 1).is_pending, True)
        # 1 Book instance also added as parent. In Pending
        self.assertEquals(Book.objects.count(), 1)
        self.assertEquals(Book.objects.get(pk = 1).is_pending, True)
        # The Book instance is pointed by book_ptr in EBook instance
        eb1 = EBook.objects.get(pk = 1)
        self.assertEquals(getattr(eb1, 'book_ptr', None) is None, False)

        # Now moderator try moderation by http_request
        self.client.logout()
        logged_in = self.client.login(username = 'moder', password = 'moder')
        self.assertEquals(logged_in, True)
        url = '/admin/test_app/ebook/'
        data = {'action': 'approve_selected', 'index': 0, '_selected_action': 1}
        response = self.client.post(url, data, follow = True)
        self.assertEquals(response.status_code, 200)
        eb1 = EBook.objects.get(pk = 1)
        self.assertEquals(eb1.is_approved, True)
        self.assertEquals(eb1.book_ptr.is_approved, True)

    def test_5_auto_delete_monitor_entries(self):
        """
        When an instance of a moderated model is deleted, the monitor entries
        corresponding to the instance and all of its parent instances also
        should be deleted.
        """
        from django_monitor.models import MonitorEntry

        self.assertEquals(MonitorEntry.objects.count(), 0)
        ebook_ct = ContentType.objects.get_for_model(EBook)
        book_ct = ContentType.objects.get_for_model(Book)

        pub1 = Publisher.objects.create(
            name = 'test_pub', num_awards = 3
        )
        auth1 = Author.objects.create(
           name = 'test_auth', age = 34
        )
        eb1 = EBook.objects.create(
            isbn = '123456789', name = 'test_ebook', 
            pages = 300, publisher = pub1
        )
        eb1.authors = [auth1]
        eb1.save()

        # 1 monitor_entry each for auth1, eb1 & its parent, eb1.book_ptr.
        self.assertEquals(MonitorEntry.objects.count(), 3)
        ebook_mes = MonitorEntry.objects.filter(content_type = ebook_ct)
        book_mes = MonitorEntry.objects.filter(content_type = book_ct)
        self.assertEquals(ebook_mes.count(), 1)
        self.assertEquals(book_mes.count(), 1)

        eb1.delete()
        # MonitorEntry object for auth1 remains. Others removed.
        self.assertEquals(MonitorEntry.objects.count(), 1)
        ebook_mes = MonitorEntry.objects.filter(content_type = ebook_ct)
        book_mes = MonitorEntry.objects.filter(content_type = book_ct)
        self.assertEquals(ebook_mes.count(), 0)
        self.assertEquals(book_mes.count(), 0) 

    def test_6_moderation_signal(self):
        """
        Make sure that a post_moderation signal is emitted.
        We have an attribute, `signal_emitted` in the model, ``Author``.
        By default, it will be set to False. When a ``post_moderation`` signal
        is emitted, a function, ``auth_post_moderation_handler`` defined in
        test_app.models will set it to True.
        """
        auth1 = Author.objects.create(
            name = "test_auth", age = 34
        )
        # Creation itself invokes moderation which in turn emits the signal.
        auth1 = Author.objects.get(pk = 1)
        self.assertEquals(auth1.signal_emitted, True)

    def test_7_moderation_queue_count(self):
        """
        moderation queue counts all pending or challenged objects of each
        monitored model and displays those counts in the changelist. The
        developer may have written some of the model_admins in a way that a
        user is able to view only a subset of all objects. eg, only those
        objects the user has created herself. Our queue should respect such
        customizations. So the counts must be prepared only after consulting
        the model_admin.queryset.
        """
        reader1 = Reader.objects.create(name = 'r1', user = self.adder)
        reader2 = Reader.objects.create(name = 'r2', user = self.adder)
        reader3 = Reader.objects.create(name = 'r3', user = self.moderator)
        reader4 = Reader.objects.create(name = 'r4', user = self.moderator)
        reader5 = Reader.objects.create(name = 'r5', user = self.moderator)
        # User 1, adder logs in
        logged_in = self.client.login(username = 'adder', password = 'adder')
        self.assertEquals(logged_in, True)
        # model_admin allows user to view just 2 objects that belong to her.
        response = self.client.get('/admin/test_app/reader/', follow = True)
        self.assertEquals(response.status_code, 200)
        result_count = len(response.context[-1]['cl'].result_list)
        self.assertEquals(result_count, 2)
        # Now is the time to test monitor_queue. Same result expected.
        response = self.client.get(
            '/admin/django_monitor/monitorentry/', follow = True
        )
        self.assertEquals(response.status_code, 200)
        queued_reader = filter(
            lambda x: x['model_name'] == 'reader',
            response.context[-1]['model_list']
        )[0]
        self.assertEquals(queued_reader['pending'], 2)
        self.assertEquals(queued_reader['challenged'], 0)
        self.client.logout()

        # User 2, moderator, repeats the same.
        logged_in = self.client.login(username = 'moder', password = 'moder')
        self.assertEquals(logged_in, True)
        response = self.client.get(
            '/admin/django_monitor/monitorentry/', follow = True
        )
        self.assertEquals(response.status_code, 200)
        queued_reader = filter(
            lambda x: x['model_name'] == 'reader',
            response.context[-1]['model_list']
        )[0]
        self.assertEquals(queued_reader['pending'], 3)
        self.assertEquals(queued_reader['challenged'], 0)
        self.client.logout()
