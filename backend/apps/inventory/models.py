from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
from decimal import Decimal

class Category(models.Model):
    """Catégories d'articles d'inventaire"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Nom'), max_length=100, unique=True)
    description = models.TextField(_('Description'), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_('Catégorie parent')
    )
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Catégorie')
        verbose_name_plural = _('Catégories')
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

class Supplier(models.Model):
    """Fournisseurs"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    name = models.CharField(_('Nom'), max_length=200)
    contact_person = models.CharField(_('Personne de contact'), max_length=200, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    phone = models.CharField(_('Téléphone'), max_length=20, blank=True)
    
    # Adresse
    address_line1 = models.CharField(_('Adresse ligne 1'), max_length=200, blank=True)
    address_line2 = models.CharField(_('Adresse ligne 2'), max_length=200, blank=True)
    city = models.CharField(_('Ville'), max_length=100, blank=True)
    postal_code = models.CharField(_('Code postal'), max_length=20, blank=True)
    country = models.CharField(_('Pays'), max_length=100, default='France')
    
    # Informations commerciales
    tax_id = models.CharField(_('Numéro fiscal'), max_length=50, blank=True)
    payment_terms = models.CharField(_('Conditions de paiement'), max_length=200, blank=True)
    
    # Évaluation
    rating = models.PositiveIntegerField(
        _('Évaluation'),
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        help_text=_('Note sur 5')  # type: ignore[attr-defined]
    )
    notes = models.TextField(_('Notes'), blank=True)
    
    # Statut
    is_active = models.BooleanField(_('Actif'), default=True)  # type: ignore[attr-defined]
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    
    class Meta:
        verbose_name = _('Fournisseur')
        verbose_name_plural = _('Fournisseurs')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    """Articles d'inventaire"""
    
    UNIT_CHOICES = [
        ('piece', _('Pièce')),
        ('kg', _('Kilogramme')),
        ('g', _('Gramme')),
        ('l', _('Litre')),
        ('ml', _('Millilitre')),
        ('m', _('Mètre')),
        ('cm', _('Centimètre')),
        ('box', _('Boîte')),
        ('pack', _('Pack')),
        ('bottle', _('Bouteille')),
        ('can', _('Boîte de conserve')),
        ('bag', _('Sac')),
    ]
    
    STATUS_CHOICES = [
        ('in_stock', _('En stock')),
        ('low_stock', _('Stock faible')),
        ('out_of_stock', _('Rupture de stock')),
        ('discontinued', _('Arrêté')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    name = models.CharField(_('Nom'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    sku = models.CharField(_('Code SKU'), max_length=50, unique=True, blank=True)
    barcode = models.CharField(_('Code-barres'), max_length=50, blank=True)
    
    # Stock
    current_stock = models.DecimalField(
        _('Stock actuel'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    minimum_stock = models.DecimalField(
        _('Stock minimum'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    maximum_stock = models.DecimalField(
        _('Stock maximum'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    unit = models.CharField(_('Unité'), max_length=20, choices=UNIT_CHOICES, default='piece')
    
    # Coûts
    unit_cost = models.DecimalField(
        _('Coût unitaire'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    total_value = models.DecimalField(
        _('Valeur totale'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Localisation
    location = models.CharField(_('Emplacement'), max_length=200, blank=True)
    shelf = models.CharField(_('Étagère'), max_length=50, blank=True)
    
    # Dates importantes
    expiry_date = models.DateField(_('Date d\'expiration'), null=True, blank=True)
    last_restocked = models.DateTimeField(_('Dernier réapprovisionnement'), null=True, blank=True)
    
    # Fournisseur
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='supplied_items'
    )
    
    # Statut
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='in_stock')
    is_active = models.BooleanField(_('Actif'), default=True)  # type: ignore[attr-defined]
    
    # Image
    image = models.ImageField(_('Image'), upload_to='inventory/', null=True, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name='created_items'
    )
    
    class Meta:
        verbose_name = _('Article d\'inventaire')
        verbose_name_plural = _('Articles d\'inventaire')
        ordering = ['name']
        permissions = [
            ('can_manage_inventory', 'Peut gérer l\'inventaire'),
            ('can_view_costs', 'Peut voir les coûts'),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Calcule automatiquement la valeur totale et le statut"""
        if self.unit_cost and self.current_stock:
            self.total_value = self.unit_cost * self.current_stock  # type: ignore[attr-defined]
        
        # Mise à jour du statut basé sur le stock
        if self.current_stock <= 0:
            self.status = 'out_of_stock'
        elif self.current_stock <= self.minimum_stock:
            self.status = 'low_stock'
        else:
            self.status = 'in_stock'
        
        # Génération automatique du SKU
        if not self.sku:
            self.sku = f"INV-{str(self.id)[:8]}"
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Vérifie si l'article est expiré"""
        if self.expiry_date:
            from datetime import date
            return self.expiry_date < date.today()
        return False
    
    @property
    def days_until_expiry(self):
        """Nombre de jours avant expiration"""
        if self.expiry_date:
            from datetime import date
            return (self.expiry_date - date.today()).days  # type: ignore[attr-defined]
        return None

class StockMovement(models.Model):
    """Mouvements de stock"""
    
    MOVEMENT_TYPES = [
        ('in', _('Entrée')),
        ('out', _('Sortie')),
        ('adjustment', _('Ajustement')),
        ('transfer', _('Transfert')),
        ('loss', _('Perte')),
        ('donation', _('Don')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movements')
    
    # Détails du mouvement
    movement_type = models.CharField(_('Type de mouvement'), max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(
        _('Quantité'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    unit_cost = models.DecimalField(
        _('Coût unitaire'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Références
    reference_number = models.CharField(_('Numéro de référence'), max_length=100, blank=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Raison et notes
    reason = models.CharField(_('Raison'), max_length=200, blank=True)
    notes = models.TextField(_('Notes'), blank=True)
    
    # Dates
    movement_date = models.DateTimeField(_('Date du mouvement'))
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stock_movements'
    )
    
    class Meta:
        verbose_name = _('Mouvement de stock')
        verbose_name_plural = _('Mouvements de stock')
        ordering = ['-movement_date']
    
    def __str__(self):
        return f"{self.item.name} - {self.get_movement_type_display()} - {self.quantity}"  # type: ignore[attr-defined]
    
    def save(self, *args, **kwargs):
        """Met à jour le stock de l'article"""
        is_new = self.pk is None
        
        if is_new:
            # Nouveau mouvement
            if self.movement_type == 'in':
                self.item.current_stock += self.quantity  # type: ignore[attr-defined]
            elif self.movement_type in ['out', 'loss']:
                self.item.current_stock -= self.quantity  # type: ignore[attr-defined]
            elif self.movement_type == 'adjustment':
                # Pour les ajustements, la quantité représente la nouvelle valeur
                self.item.current_stock = self.quantity  # type: ignore[attr-defined]
            
            # Mise à jour de la date de réapprovisionnement
            if self.movement_type == 'in':
                self.item.last_restocked = self.movement_date  # type: ignore[attr-defined] 
            
            self.item.save()  # type: ignore[attr-defined]
        
        super().save(*args, **kwargs)

class PurchaseOrder(models.Model):
    """Commandes d'achat"""
    
    STATUS_CHOICES = [
        ('draft', _('Brouillon')),
        ('sent', _('Envoyée')),
        ('confirmed', _('Confirmée')),
        ('partially_received', _('Partiellement reçue')),
        ('received', _('Reçue')),
        ('cancelled', _('Annulée')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    order_number = models.CharField(_('Numéro de commande'), max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    
    # Dates
    order_date = models.DateTimeField(_('Date de commande'))
    expected_delivery_date = models.DateField(_('Date de livraison prévue'), null=True, blank=True)
    actual_delivery_date = models.DateField(_('Date de livraison réelle'), null=True, blank=True)
    
    # Montants
    subtotal = models.DecimalField(_('Sous-total'), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(_('Montant des taxes'), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_('Montant total'), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Statut
    status = models.CharField(_('Statut'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Notes
    notes = models.TextField(_('Notes'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Créé le'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Modifié le'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_purchase_orders'
    )
    
    class Meta:
        verbose_name = _('Commande d\'achat')
        verbose_name_plural = _('Commandes d\'achat')
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        """Génère automatiquement le numéro de commande"""
        if not self.order_number:
            from datetime import datetime
            self.order_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

class PurchaseOrderItem(models.Model):
    """Articles d'une commande d'achat"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    
    # Quantités
    quantity_ordered = models.DecimalField(
        _('Quantité commandée'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    quantity_received = models.DecimalField(
        _('Quantité reçue'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Prix
    unit_price = models.DecimalField(
        _('Prix unitaire'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    total_price = models.DecimalField(
        _('Prix total'),
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Notes
    notes = models.TextField(_('Notes'), blank=True)
    
    class Meta:
        verbose_name = _('Article de commande')
        verbose_name_plural = _('Articles de commande')
        unique_together = ['purchase_order', 'item']
    
    def __str__(self):
        return f"{self.item.name} - {self.quantity_ordered}"
    
    def save(self, *args, **kwargs):
        """Calcule automatiquement le prix total"""
        self.total_price = self.quantity_ordered * self.unit_price  # type: ignore[attr-defined]
        super().save(*args, **kwargs)
    
    @property
    def is_fully_received(self):
        """Vérifie si l'article est entièrement reçu"""
        return self.quantity_received >= self.quantity_ordered
