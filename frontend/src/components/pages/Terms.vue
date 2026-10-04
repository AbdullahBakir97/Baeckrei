<template>
  <LegalPage :title="$t('legal.terms.title')" :updated="$t('legal.updatedDate')">
    <template v-if="locale === 'de'">
      <h2>1. Geltungsbereich</h2>
      <p>
        Diese Bedingungen gelten für alle Bestellungen im Onlineshop von {{ business.legalName || business.name }},
        {{ address }} („wir“).
      </p>

      <h2>2. Vertragsschluss</h2>
      <p>
        Die Produkte im Shop sind eine Aufforderung zur Bestellung. Mit einem Klick auf „Zahlungspflichtig bestellen“
        gibst du ein verbindliches Angebot ab. Der Vertrag kommt zustande, wenn wir die Bestellung bestätigen,
        spätestens mit der Übergabe der Ware.
      </p>

      <h2>3. Preise</h2>
      <p>Alle Preise sind in Euro und enthalten die gesetzliche Mehrwertsteuer. Eine Liefergebühr wird dir vor der Bestellung an der Kasse angezeigt.</p>

      <h2>4. Abholung und Lieferung</h2>
      <p>
        Du kannst deine Bestellung in unserem Laden abholen ({{ address }}<template v-if="business.transit">, {{ business.transit }}</template>)
        oder liefern lassen. Eine gewünschte Zeit ist ein Wunsch; wenn wir sie nicht einhalten können, melden wir uns bei dir.
      </p>

      <h2>5. Bezahlung</h2>
      <p>Du bezahlst bar oder mit Karte bei Abholung oder Lieferung.</p>

      <h2 id="withdrawal">6. Stornierung und Widerrufsrecht</h2>
      <p>
        Du kannst eine Bestellung kostenlos in deinem Konto stornieren, solange sie noch nicht vorbereitet wurde.
        Unsere Produkte sind frische Backwaren, die schnell verderben; das gesetzliche Widerrufsrecht besteht daher
        nicht (§ 312g Abs. 2 Nr. 2 BGB).
      </p>

      <h2>7. Allergene</h2>
      <p>Zutaten und Allergene stehen auf jeder Produktseite. Wenn du eine Allergie hast, sprich uns bitte vor der Bestellung an.</p>

      <h2>8. Gewährleistung</h2>
      <p>Es gelten die gesetzlichen Gewährleistungsrechte. Bitte melde dich so schnell wie möglich, wenn mit deiner Bestellung etwas nicht stimmt.</p>
    </template>

    <template v-else-if="locale === 'ar'">
      <p class="text-sm text-gray-500">هذه ترجمة للتسهيل؛ النسخة الألمانية هي النسخة الملزمة قانونيًا.</p>

      <h2>1. نطاق التطبيق</h2>
      <p>
        تسري هذه الشروط على جميع الطلبات المقدَّمة عبر المتجر الإلكتروني لـ {{ business.legalName || business.name }}،
        {{ address }} («نحن»).
      </p>

      <h2>2. تقديم الطلب</h2>
      <p>
        تُعدّ المنتجات المعروضة في المتجر دعوةً إلى تقديم الطلب. وبالنقر على «تقديم الطلب» تقدّم عرضًا ملزمًا.
        وينعقد العقد عند تأكيدنا للطلب، وفي موعد أقصاه تسليمنا للبضاعة.
      </p>

      <h2>3. الأسعار</h2>
      <p>جميع الأسعار باليورو وتشمل ضريبة القيمة المضافة المقرّرة قانونًا. وتُعرض رسوم التوصيل عند إتمام الشراء قبل تقديم الطلب.</p>

      <h2>4. الاستلام والتوصيل</h2>
      <p>
        يمكنك استلام طلبك من متجرنا ({{ address }}<template v-if="business.transit">، {{ business.transit }}</template>) أو طلب توصيله إليك.
        ويُعدّ الوقت المطلوب رغبةً تفضيلية؛ وسنتواصل معك إذا تعذّر علينا الالتزام به.
      </p>

      <h2>5. الدفع</h2>
      <p>تدفع نقدًا أو بالبطاقة عند استلامك الطلب أو تسلّمه.</p>

      <h2 id="withdrawal">6. الإلغاء وحق العدول</h2>
      <p>
        يمكنك إلغاء الطلب مجانًا من خلال حسابك ما دام لم يُجهَّز بعد.
        منتجاتنا مخبوزات طازجة سريعة التلف؛ ولذلك لا ينطبق حق العدول المقرّر قانونًا
        وفقًا للقانون المدني الألماني (§ 312g (2) no. 2 BGB).
      </p>

      <h2>7. مسبّبات الحساسية</h2>
      <p>المكوّنات ومسبّبات الحساسية مدرجة في صفحة كل منتج. إذا كنت تعاني من حساسية، فيُرجى التواصل معنا قبل تقديم الطلب.</p>

      <h2>8. الضمان</h2>
      <p>تسري حقوق الضمان المقرّرة قانونًا. يُرجى إبلاغنا بأي مشكلة في طلبك في أقرب وقت ممكن.</p>
    </template>

    <template v-else>
      <h2>1. Scope</h2>
      <p>
        These terms apply to all orders placed in the online shop of {{ business.legalName || business.name }},
        {{ address }} ("we").
      </p>

      <h2>2. Placing an order</h2>
      <p>
        Products in the shop are an invitation to order. By clicking "Place order" you make a binding offer.
        The contract is formed when we confirm the order, at the latest when we hand over the goods.
      </p>

      <h2>3. Prices</h2>
      <p>All prices are in euros and include the statutory VAT. A delivery fee is shown at checkout before you order.</p>

      <h2>4. Pickup and delivery</h2>
      <p>
        You can pick up your order at our shop ({{ address }}<template v-if="business.transit">, {{ business.transit }}</template>) or have it delivered.
        A requested time is a preference; we will contact you if we cannot meet it.
      </p>

      <h2>5. Payment</h2>
      <p>You pay in cash or by card when you pick up or receive the order.</p>

      <h2 id="withdrawal">6. Cancellation and right of withdrawal</h2>
      <p>
        You can cancel an order free of charge in your account as long as it has not been prepared.
        Our products are fresh baked goods that spoil quickly; the statutory right of withdrawal therefore
        does not apply (§ 312g (2) no. 2 BGB).
      </p>

      <h2>7. Allergens</h2>
      <p>Ingredients and allergens are listed on each product page. If you have an allergy, please contact us before ordering.</p>

      <h2>8. Warranty</h2>
      <p>The statutory warranty rights apply. Please tell us about any problem with your order as soon as possible.</p>
      <p class="text-sm text-gray-500">{{ $t('legal.germanBinding') }}</p>
    </template>
  </LegalPage>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LegalPage from '@/components/legal/LegalPage.vue'
import { business, streetLine, cityLine } from '@/config/business'

const { locale } = useI18n()
const address = computed(() => [streetLine(), cityLine()].filter(Boolean).join(', '))
</script>
