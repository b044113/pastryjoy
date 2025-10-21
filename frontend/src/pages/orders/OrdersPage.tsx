import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Layout } from '../../components/layout/Layout';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Loading } from '../../components/common/Loading';
import { orderService } from '../../services/order.service';
import { productService } from '../../services/product.service';
import { useAuth } from '../../contexts/AuthContext';
import type { Order, Product } from '../../types';

export const OrdersPage: React.FC = () => {
  const { t } = useTranslation();
  const { isAdmin } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isStatusModalOpen, setIsStatusModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [formData, setFormData] = useState({
    customer_name: '',
    customer_email: '',
    notes: '',
    items: [] as { product_id: string; quantity: number; unit_price: number }[],
  });
  const [statusUpdate, setStatusUpdate] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // For adding items to order
  const [selectedProductId, setSelectedProductId] = useState('');
  const [itemQuantity, setItemQuantity] = useState('1');
  const [itemPrice, setItemPrice] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [ordersData, productsData] = await Promise.all([
        orderService.getAll(),
        productService.getAll(),
      ]);
      setOrders(ordersData);
      setProducts(productsData);
    } catch (err: any) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = () => {
    setFormData({
      customer_name: '',
      customer_email: '',
      notes: '',
      items: [],
    });
    setSelectedProductId('');
    setItemQuantity('1');
    setItemPrice('');
    setError('');
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setFormData({
      customer_name: '',
      customer_email: '',
      notes: '',
      items: [],
    });
    setSelectedProductId('');
    setItemQuantity('1');
    setItemPrice('');
    setError('');
  };

  const handleOpenStatusModal = (order: Order) => {
    setSelectedOrder(order);
    setStatusUpdate(order.status);
    setIsStatusModalOpen(true);
  };

  const handleCloseStatusModal = () => {
    setIsStatusModalOpen(false);
    setSelectedOrder(null);
    setStatusUpdate('');
  };

  const handleAddItem = () => {
    if (!selectedProductId || !itemQuantity || !itemPrice) {
      setError(t('orders.selectProductQtyPrice'));
      return;
    }

    const quantity = parseFloat(itemQuantity);
    const price = parseFloat(itemPrice);

    if (quantity <= 0 || price < 0) {
      setError(t('orders.qtyPriceValidation'));
      return;
    }

    // Check if product already added
    if (formData.items.some((item) => item.product_id === selectedProductId)) {
      setError(t('orders.productAlreadyAdded'));
      return;
    }

    setFormData({
      ...formData,
      items: [
        ...formData.items,
        { product_id: selectedProductId, quantity, unit_price: price },
      ],
    });
    setSelectedProductId('');
    setItemQuantity('1');
    setItemPrice('');
    setError('');
  };

  const handleRemoveItem = (productId: string) => {
    setFormData({
      ...formData,
      items: formData.items.filter((item) => item.product_id !== productId),
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.items.length === 0) {
      setError(t('orders.itemsRequired'));
      return;
    }

    setSubmitting(true);

    try {
      await orderService.create({
        customer_name: formData.customer_name,
        customer_email: formData.customer_email,
        notes: formData.notes || undefined,
        items: formData.items,
      });
      await loadData();
      handleCloseModal();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errors.generic'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdateStatus = async () => {
    if (!selectedOrder) return;

    setSubmitting(true);
    try {
      await orderService.updateStatus(selectedOrder.id, {
        status: statusUpdate as any,
      });
      await loadData();
      handleCloseStatusModal();
    } catch (err: any) {
      alert(err.response?.data?.detail || t('orders.statusUpdateFailed'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t('orders.deleteConfirm'))) return;

    try {
      await orderService.delete(id);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || t('errors.generic'));
    }
  };

  const getProductName = (productId: string): string => {
    const product = products.find((prod) => prod.id === productId);
    return product?.name || t('orders.unknown');
  };

  const getStatusBadgeColor = (status: string): string => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-purple-100 text-purple-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const calculateOrderTotal = (): number => {
    return formData.items.reduce(
      (sum, item) => sum + item.quantity * item.unit_price,
      0
    );
  };

  if (loading) return <Loading fullScreen />;

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{t('orders.title')}</h1>
            <p className="text-gray-600 mt-2">
              {isAdmin() ? t('orders.manageAllOrders') : t('orders.viewYourOrders')}
            </p>
          </div>
          <Button onClick={handleOpenModal}>+ {t('orders.createOrder')}</Button>
        </div>

        {orders.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📦</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {t('orders.noOrdersYet')}
              </h3>
              <p className="text-gray-600 mb-6">
                {t('orders.getStarted')}
              </p>
              <Button onClick={handleOpenModal}>{t('orders.createFirstOrder')}</Button>
            </div>
          </Card>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <Card key={order.id} className="hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {order.customer_name}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeColor(
                          order.status
                        )}`}
                      >
                        {t(`orders.statuses.${order.status}`)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{order.customer_email}</p>
                    {order.notes && (
                      <p className="text-sm text-gray-500 mt-1 italic">
                        {t('orders.note')}: {order.notes}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary-600">
                      ${order.total.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(order.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                {/* Order Items */}
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    {t('orders.items')} ({order.items.length}):
                  </p>
                  <div className="space-y-1">
                    {order.items.map((item) => (
                      <div
                        key={item.id}
                        className="flex justify-between text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded"
                      >
                        <span>
                          {item.product_name || t('products.product')} × {item.quantity}
                        </span>
                        <span className="font-medium">
                          ${item.total.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {isAdmin() && (
                    <>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleOpenStatusModal(order)}
                      >
                        {t('orders.updateStatus')}
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(order.id)}
                      >
                        {t('common.delete')}
                      </Button>
                    </>
                  )}
                  {!isAdmin() && order.status === 'pending' && (
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(order.id)}
                    >
                      {t('orders.cancelOrder')}
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Create Order Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          title={t('orders.createOrder')}
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={handleCloseModal}>
                {t('common.cancel')}
              </Button>
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting ? t('orders.creating') : t('orders.createOrder')}
              </Button>
            </>
          }
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label={t('orders.customerName')}
              value={formData.customer_name}
              onChange={(e) =>
                setFormData({ ...formData, customer_name: e.target.value })
              }
              required
              disabled={submitting}
            />

            <Input
              label={t('orders.customerEmail')}
              type="email"
              value={formData.customer_email}
              onChange={(e) =>
                setFormData({ ...formData, customer_email: e.target.value })
              }
              required
              disabled={submitting}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('orders.notes')}
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) =>
                  setFormData({ ...formData, notes: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows={3}
                disabled={submitting}
              />
            </div>

            {/* Add Items Section */}
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3">
                {t('orders.orderItems')}
              </h4>

              <div className="flex gap-2 mb-3">
                <select
                  value={selectedProductId}
                  onChange={(e) => setSelectedProductId(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  disabled={submitting}
                >
                  <option value="">{t('orders.selectProduct')}</option>
                  {products.map((prod) => (
                    <option key={prod.id} value={prod.id}>
                      {prod.name}
                    </option>
                  ))}
                </select>

                <Input
                  type="number"
                  step="0.001"
                  placeholder={t('products.qty')}
                  value={itemQuantity}
                  onChange={(e) => setItemQuantity(e.target.value)}
                  disabled={submitting}
                  className="w-24"
                />

                <Input
                  type="number"
                  step="0.01"
                  placeholder={t('common.price')}
                  value={itemPrice}
                  onChange={(e) => setItemPrice(e.target.value)}
                  disabled={submitting}
                  className="w-24"
                />

                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleAddItem}
                  disabled={submitting}
                >
                  {t('orders.add')}
                </Button>
              </div>

              {/* List of added items */}
              {formData.items.length > 0 && (
                <div className="space-y-2">
                  {formData.items.map((item) => (
                    <div
                      key={item.product_id}
                      className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-lg"
                    >
                      <span className="text-sm">
                        {getProductName(item.product_id)} - {item.quantity} ×{' '}
                        ${item.unit_price.toFixed(2)} = $
                        {(item.quantity * item.unit_price).toFixed(2)}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveItem(item.product_id)}
                        className="text-red-600 hover:text-red-700 text-sm"
                        disabled={submitting}
                      >
                        {t('orders.remove')}
                      </button>
                    </div>
                  ))}

                  <div className="flex justify-between items-center pt-2 border-t">
                    <span className="font-medium text-gray-900">{t('common.total')}:</span>
                    <span className="text-xl font-bold text-primary-600">
                      ${calculateOrderTotal().toFixed(2)}
                    </span>
                  </div>
                </div>
              )}

              {formData.items.length === 0 && (
                <p className="text-sm text-gray-500 italic">
                  {t('orders.noItemsYet')}
                </p>
              )}
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
          </form>
        </Modal>

        {/* Update Status Modal */}
        <Modal
          isOpen={isStatusModalOpen}
          onClose={handleCloseStatusModal}
          title={t('orders.updateOrderStatus')}
          footer={
            <>
              <Button variant="secondary" onClick={handleCloseStatusModal}>
                {t('common.cancel')}
              </Button>
              <Button onClick={handleUpdateStatus} disabled={submitting}>
                {submitting ? t('orders.updating') : t('orders.updateStatus')}
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              {t('orders.order')}: {selectedOrder?.customer_name}
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('common.status')}
              </label>
              <select
                value={statusUpdate}
                onChange={(e) => setStatusUpdate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                disabled={submitting}
              >
                <option value="pending">{t('orders.statuses.pending')}</option>
                <option value="confirmed">{t('orders.statuses.confirmed')}</option>
                <option value="in_progress">{t('orders.statuses.in_progress')}</option>
                <option value="completed">{t('orders.statuses.completed')}</option>
                <option value="cancelled">{t('orders.statuses.cancelled')}</option>
              </select>
            </div>
          </div>
        </Modal>
      </div>
    </Layout>
  );
};
