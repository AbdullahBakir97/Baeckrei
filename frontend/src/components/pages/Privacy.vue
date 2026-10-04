<template>
  <LegalPage :title="$t('legal.privacy.title')" :updated="$t('legal.updatedDate')">
    <!-- German is the binding version; English is provided for convenience. -->
    <template v-if="locale === 'de'">
      <h2>Verantwortlicher</h2>
      <p>
        {{ business.legalName || business.name }}, {{ address }}.
        E-Mail: <Fill :value="business.email" :label="$t('legal.fields.email')" />.
        Die vollständigen Kontaktdaten findest du im <router-link to="/impressum">Impressum</router-link>.
      </p>

      <h2>Welche Daten wir verarbeiten und warum</h2>
      <ul class="list-disc ps-6 space-y-2">
        <li>
          <strong class="text-white">Dein Kundenkonto</strong>: E-Mail-Adresse, Name, Telefonnummer (optional) und ein
          sicher verschlüsseltes Passwort, damit du dich anmelden und deine Bestellungen sehen kannst (Art. 6 Abs. 1 lit. b DSGVO).
        </li>
        <li>
          <strong class="text-white">Bestellungen</strong>: die bestellten Produkte, Abholung oder Lieferung, Lieferadresse,
          Wunschzeit, Hinweise und Zahlungsart, damit wir deine Bestellung vorbereiten und übergeben und unsere
          Aufbewahrungspflichten erfüllen können (Art. 6 Abs. 1 lit. b und c DSGVO).
        </li>
        <li>
          <strong class="text-white">Gespeicherte Adressen</strong>: Lieferadressen, die du in deinem Konto behalten möchtest
          (Art. 6 Abs. 1 lit. b DSGVO). Du kannst sie jederzeit in den Einstellungen löschen.
        </li>
        <li>
          <strong class="text-white">Kontaktformular und Newsletter</strong>: Name, E-Mail-Adresse und Nachricht, wenn du uns
          schreibst, und deine E-Mail-Adresse, wenn du den Newsletter abonnierst (Art. 6 Abs. 1 lit. a und b DSGVO).
          Du kannst dich jederzeit abmelden.
        </li>
        <li>
          <strong class="text-white">Technische Daten</strong>: Der Server protokolliert IP-Adresse und Zeitpunkt von Anfragen,
          um den Shop sicher zu betreiben (Art. 6 Abs. 1 lit. f DSGVO).
        </li>
      </ul>

      <h2>Bezahlung</h2>
      <p>Du bezahlst bar oder mit Karte, wenn du deine Bestellung abholst oder erhältst. Kartendaten speichern wir nicht.</p>

      <h2>Speicherdauer</h2>
      <p>
        Kontodaten speichern wir, bis du dein Konto löschst. Bestelldaten bewahren wir so lange auf, wie es steuer- und
        handelsrechtlich vorgeschrieben ist (in der Regel bis zu 10 Jahre). Kontaktanfragen löschen wir, sobald sie erledigt sind.
      </p>

      <h2>Cookies und lokaler Speicher</h2>
      <p>
        Wir verwenden nur, was für den Betrieb des Shops nötig ist. Die Schriften werden von unserem eigenen Server geladen.
        Einzelheiten findest du in unserer <router-link to="/cookie-policy">Cookie-Richtlinie</router-link>.
      </p>

      <h2>Deine Rechte</h2>
      <p>
        Du hast das Recht auf Auskunft, Berichtigung und Löschung deiner Daten, auf Einschränkung der Verarbeitung,
        auf Widerspruch, auf Datenübertragbarkeit und auf jederzeitigen Widerruf einer Einwilligung. Außerdem kannst du
        dich bei einer Datenschutz-Aufsichtsbehörde beschweren, zum Beispiel bei der Berliner Beauftragten für Datenschutz
        und Informationsfreiheit.
      </p>
    </template>

    <template v-else-if="locale === 'ar'">
      <p class="text-sm text-gray-500">هذه ترجمة للتسهيل؛ النسخة الألمانية هي النسخة الملزمة قانونيًا.</p>

      <h2>الجهة المسؤولة</h2>
      <p>
        {{ business.legalName || business.name }}، {{ address }}.
        البريد الإلكتروني: <Fill :value="business.email" :label="$t('legal.fields.email')" />.
        للاطلاع على بيانات الاتصال الكاملة، يُرجى مراجعة صفحة <router-link to="/impressum">Impressum</router-link> (البيانات القانونية للناشر).
      </p>

      <h2>البيانات التي نجمعها والغرض منها</h2>
      <ul class="list-disc ps-6 space-y-2">
        <li>
          <strong class="text-white">حسابك</strong>: عنوان البريد الإلكتروني والاسم ورقم الهاتف (اختياري) وكلمة مرور
          محفوظة بصيغة مُجزّأة (hashed) آمنة، لتتمكن من تسجيل الدخول والاطلاع على طلباتك
          (Art. 6(1)(b) GDPR – اللائحة العامة لحماية البيانات).
        </li>
        <li>
          <strong class="text-white">الطلبات</strong>: المنتجات التي تطلبها، واختيارك بين الاستلام أو التوصيل،
          وعنوان التوصيل، والوقت المفضّل، والملاحظات، وطريقة الدفع، لنتمكن من تجهيز طلبك وتسليمه
          والوفاء بالتزاماتنا المحاسبية (Art. 6(1)(b), (c) GDPR).
        </li>
        <li>
          <strong class="text-white">العناوين المحفوظة</strong>: عناوين التوصيل التي تختار الاحتفاظ بها في
          حسابك (Art. 6(1)(b) GDPR). ويمكنك حذفها في أي وقت من الإعدادات.
        </li>
        <li>
          <strong class="text-white">نموذج التواصل والنشرة الإخبارية</strong>: اسمك وعنوان بريدك الإلكتروني ورسالتك
          عند مراسلتنا، وعنوان بريدك الإلكتروني إذا اشتركت في نشرتنا الإخبارية (Art. 6(1)(a), (b)
          GDPR). ويمكنك إلغاء الاشتراك في أي وقت.
        </li>
        <li>
          <strong class="text-white">البيانات التقنية</strong>: يسجّل الخادم عنوان IP ووقت الطلبات
          للحفاظ على أمان المتجر (Art. 6(1)(f) GDPR).
        </li>
      </ul>

      <h2>الدفع</h2>
      <p>تدفع نقدًا أو بالبطاقة عند استلامك طلبك أو تسلّمه. ولا نخزّن بيانات البطاقات.</p>

      <h2>مدة الاحتفاظ بالبيانات</h2>
      <p>
        تُحفظ بيانات الحساب إلى أن تحذف حسابك. وتُحفظ سجلات الطلبات للمدة التي يقتضيها القانون الضريبي
        والتجاري (عادةً حتى 10 سنوات). وتُحذف رسائل التواصل فور الانتهاء من معالجتها.
      </p>

      <h2>ملفات تعريف الارتباط (الكوكيز) والتخزين المحلي</h2>
      <p>
        لا نستخدم إلا ما هو ضروري لتشغيل المتجر. وتُحمَّل الخطوط من خادمنا الخاص. وتجد التفاصيل في
        <router-link to="/cookie-policy">سياسة ملفات تعريف الارتباط</router-link> الخاصة بنا.
      </p>

      <h2>حقوقك</h2>
      <p>
        يحق لك الاطلاع على بياناتك وتصحيحها وحذفها، وتقييد معالجتها أو الاعتراض عليها،
        ونقلها، وسحب موافقتك في أي وقت. كما يحق لك تقديم شكوى إلى سلطة رقابية مختصة بحماية
        البيانات، ومنها على سبيل المثال مفوّض ولاية برلين لحماية البيانات وحرية المعلومات.
      </p>
    </template>

    <template v-else>
      <h2>Who is responsible</h2>
      <p>
        {{ business.legalName || business.name }}, {{ address }}.
        Email: <Fill :value="business.email" :label="$t('legal.fields.email')" />.
        See the <router-link to="/impressum">Impressum</router-link> for full contact details.
      </p>

      <h2>What we collect and why</h2>
      <ul class="list-disc ps-6 space-y-2">
        <li>
          <strong class="text-white">Your account</strong>: email address, name, phone number (optional) and a
          securely hashed password, so you can sign in and see your orders (Art. 6(1)(b) GDPR).
        </li>
        <li>
          <strong class="text-white">Orders</strong>: the products you order, pickup or delivery choice,
          delivery address, preferred time, notes and payment method, so we can prepare and hand over your
          order and meet our bookkeeping obligations (Art. 6(1)(b) and (c) GDPR).
        </li>
        <li>
          <strong class="text-white">Saved addresses</strong>: delivery addresses you choose to keep in your
          account (Art. 6(1)(b) GDPR). You can delete them at any time in your settings.
        </li>
        <li>
          <strong class="text-white">Contact form and newsletter</strong>: your name, email address and message
          when you write to us, and your email address if you subscribe to our newsletter (Art. 6(1)(a) and (b)
          GDPR). You can unsubscribe at any time.
        </li>
        <li>
          <strong class="text-white">Technical data</strong>: the server logs the IP address and time of requests
          to keep the shop secure (Art. 6(1)(f) GDPR).
        </li>
      </ul>

      <h2>Payment</h2>
      <p>You pay in cash or by card when you pick up or receive your order. We do not store card details.</p>

      <h2>How long we keep data</h2>
      <p>
        Account data is kept until you delete your account. Order records are kept for as long as tax and
        commercial law requires (usually up to 10 years). Contact messages are deleted once they are dealt with.
      </p>

      <h2>Cookies and local storage</h2>
      <p>
        We only use what is needed for the shop to work. Fonts are served from our own server. Details are in our
        <router-link to="/cookie-policy">cookie policy</router-link>.
      </p>

      <h2>Your rights</h2>
      <p>
        You have the right to access, correct and delete your data, to restrict or object to its processing,
        to data portability and to withdraw consent at any time. You can also complain to a data protection
        supervisory authority, for example the Berlin Commissioner for Data Protection and Freedom of Information.
      </p>
      <p class="text-sm text-gray-500">{{ $t('legal.germanBinding') }}</p>
    </template>
  </LegalPage>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LegalPage from '@/components/legal/LegalPage.vue'
import Fill from '@/components/legal/Fill.vue'
import { business, streetLine, cityLine } from '@/config/business'

const { locale } = useI18n()
const address = computed(() => [streetLine(), cityLine()].filter(Boolean).join(', '))
</script>
