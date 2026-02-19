"use client";
import { useEffect, useState } from "react";
import { Building2, Plus, MapPin, Users, Trash2 } from "lucide-react";
import { propertiesApi } from "@/lib/api";

interface Property {
  id: string;
  name: string;
  address_line1: string;
  city: string;
  state: string;
  zip_code: string;
  unit_count: number;
  auto_enroll: boolean;
  pms_property_id: string | null;
}

const STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"];

export default function PropertiesPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: "",
    address_line1: "",
    city: "",
    state: "CA",
    zip_code: "",
    unit_count: "",
    pms_property_id: "",
    auto_enroll: true,
    enrollment_delay_days: "3",
  });

  useEffect(() => {
    propertiesApi.list().then((r) => setProperties(r.data)).finally(() => setLoading(false));
  }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await propertiesApi.create({
        ...form,
        unit_count: parseInt(form.unit_count) || 0,
        enrollment_delay_days: parseInt(form.enrollment_delay_days) || 3,
      });
      setProperties([...properties, res.data]);
      setShowForm(false);
      setForm({ name: "", address_line1: "", city: "", state: "CA", zip_code: "", unit_count: "", pms_property_id: "", auto_enroll: true, enrollment_delay_days: "3" });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    await propertiesApi.delete(id);
    setProperties(properties.filter((p) => p.id !== id));
  };

  const upd = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Properties</h1>
          <p className="text-gray-500 mt-1">Manage your enrolled properties</p>
        </div>
        <button onClick={() => setShowForm(true)} className="btn-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add Property
        </button>
      </div>

      {/* Add Property Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-8 w-full max-w-lg shadow-xl">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Add Property</h2>
            <form onSubmit={handleAdd} className="space-y-4">
              <div>
                <label className="label">Property Name</label>
                <input className="input" value={form.name} onChange={(e) => upd("name", e.target.value)} placeholder="Sunset Apartments" required />
              </div>
              <div>
                <label className="label">Address</label>
                <input className="input" value={form.address_line1} onChange={(e) => upd("address_line1", e.target.value)} placeholder="123 Main St" required />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div className="col-span-1">
                  <label className="label">City</label>
                  <input className="input" value={form.city} onChange={(e) => upd("city", e.target.value)} required />
                </div>
                <div>
                  <label className="label">State</label>
                  <select className="input" value={form.state} onChange={(e) => upd("state", e.target.value)}>
                    {STATES.map((s) => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="label">ZIP</label>
                  <input className="input" value={form.zip_code} onChange={(e) => upd("zip_code", e.target.value)} required />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label">Total Units</label>
                  <input type="number" className="input" value={form.unit_count} onChange={(e) => upd("unit_count", e.target.value)} />
                </div>
                <div>
                  <label className="label">PMS Property ID</label>
                  <input className="input" value={form.pms_property_id} onChange={(e) => upd("pms_property_id", e.target.value)} placeholder="Optional" />
                </div>
              </div>
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="auto_enroll"
                  checked={form.auto_enroll}
                  onChange={(e) => upd("auto_enroll", e.target.checked)}
                  className="h-4 w-4 text-brand-600"
                />
                <label htmlFor="auto_enroll" className="text-sm text-gray-700">
                  Auto-enroll new residents (recommended)
                </label>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1 justify-center">Cancel</button>
                <button type="submit" className="btn-primary flex-1 justify-center" disabled={saving}>
                  {saving ? "Adding..." : "Add Property"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Property List */}
      {loading ? (
        <div className="text-center py-12 text-gray-400">Loading...</div>
      ) : properties.length === 0 ? (
        <div className="text-center py-20">
          <Building2 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No properties yet</h3>
          <p className="text-gray-500 mb-6">Add your first property to start enrolling residents</p>
          <button onClick={() => setShowForm(true)} className="btn-primary">Add First Property</button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {properties.map((prop) => (
            <div key={prop.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="bg-brand-50 p-2.5 rounded-lg">
                  <Building2 className="h-5 w-5 text-brand-600" />
                </div>
                <button
                  onClick={() => handleDelete(prop.id)}
                  className="text-gray-300 hover:text-red-500 transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <h3 className="font-semibold text-gray-900">{prop.name}</h3>
              <div className="flex items-center gap-1 text-gray-500 text-sm mt-1">
                <MapPin className="h-3.5 w-3.5" />
                {prop.address_line1}, {prop.city}, {prop.state} {prop.zip_code}
              </div>
              <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-50">
                <div className="flex items-center gap-1 text-sm text-gray-500">
                  <Users className="h-3.5 w-3.5" />
                  {prop.unit_count} units
                </div>
                {prop.auto_enroll && (
                  <span className="badge bg-green-100 text-green-700">Auto-enroll</span>
                )}
                {prop.pms_property_id && (
                  <span className="badge bg-blue-100 text-blue-700">PMS linked</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
