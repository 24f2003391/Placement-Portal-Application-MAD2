<script setup>
import { ref, onMounted } from 'vue'
import { useMessageStore } from '@/stores/messageStore'

const messageStore = useMessageStore()

const companies = ref([])
const loading = ref(false)

const search = ref({
  name: '',
  industry: '',
  hr_phone: '',
  website: '',
  approval_status: '',
  is_blacklisted: ''
})

// 🔹 Fetch companies
async function fetchCompanies() {
  loading.value = true

  try {
    const params = new URLSearchParams()

    Object.entries(search.value).forEach(([key, value]) => {
      if (value !== '' && value !== null) {
        params.append(key, value)
      }
    })

    const res = await fetch(`http://127.0.0.1:5000/api/admin/companies?${params}`)
    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Failed to fetch companies')
      return
    }

    // 🔥 Sort order: Approved → Applied → Rejected
    const order = { Approved: 1, Applied: 2, Rejected: 3 }

    companies.value = data.sort((a, b) => {
      return order[a.approval_status] - order[b.approval_status]
    })

  } catch (err) {
    messageStore.updateMessages('Something went wrong while fetching companies')
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 🔹 Perform action
async function performAction(id, action) {
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/admin/companies/action/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    })

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Action failed')
      return
    }

    messageStore.updateMessages(data.message)
    fetchCompanies()

  } catch (err) {
    messageStore.updateMessages('Something went wrong while performing action')
    console.error(err)
  }
}

onMounted(fetchCompanies)
</script>

<template>
  <div class="container mt-4">

    <h2 class="mb-3">Admin Dashboard - Companies</h2>

    <!-- 🔍 Search -->
    <div class="row g-2 mb-3">
      <div class="col">
        <input v-model="search.name" class="form-control" placeholder="Name">
      </div>

      <div class="col">
        <input v-model="search.industry" class="form-control" placeholder="Industry">
      </div>

      <div class="col">
        <input v-model="search.hr_phone" class="form-control" placeholder="Phone">
      </div>

      <div class="col">
        <input v-model="search.website" class="form-control" placeholder="Website">
      </div>

      <div class="col">
        <select v-model="search.approval_status" class="form-select">
          <option value="">All Status</option>
          <option value="Approved">Approved</option>
          <option value="Applied">Applied</option>
          <option value="Rejected">Rejected</option>
        </select>
      </div>

      <div class="col">
        <select v-model="search.is_blacklisted" class="form-select">
          <option value="">Blacklist</option>
          <option value="true">Blacklisted</option>
          <option value="false">Active</option>
        </select>
      </div>

      <div class="col">
        <button class="btn btn-primary w-100" @click="fetchCompanies">
          Search
        </button>
      </div>
    </div>

    <!-- 🔄 Loading -->
    <div v-if="loading" class="text-center">
      Loading...
    </div>

    <!-- 📊 Table -->
    <table v-if="!loading" class="table table-bordered table-hover">
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Industry</th>
          <th>Phone</th>
          <th>Website</th>
          <th>Status</th>
          <th>Blacklisted</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="c in companies" :key="c.id">
          <td>{{ c.id }}</td>
          <td>{{ c.name }}</td>
          <td>{{ c.industry }}</td>
          <td>{{ c.hr_phone }}</td>
          <td>{{ c.website }}</td>

          <!-- Status -->
          <td>
            <span 
              :class="{
                'badge bg-success': c.approval_status === 'Approved',
                'badge bg-warning text-dark': c.approval_status === 'Applied',
                'badge bg-danger': c.approval_status === 'Rejected'
              }"
            >
              {{ c.approval_status }}
            </span>
          </td>

          <!-- Blacklist -->
          <td>
            <span :class="c.is_blacklisted ? 'text-danger' : 'text-success'">
              {{ c.is_blacklisted ? 'Yes' : 'No' }}
            </span>
          </td>

          <!-- Actions -->
          <td>

            <!-- Applied -->
            <div v-if="c.approval_status === 'Applied'">
              <button class="btn btn-success btn-sm me-2"
                @click="performAction(c.id, 'approve')">
                Approve
              </button>

              <button class="btn btn-danger btn-sm"
                @click="performAction(c.id, 'reject')">
                Reject
              </button>
            </div>

            <!-- Approved -->
            <div v-else-if="c.approval_status === 'Approved'">

              <button class="btn btn-warning btn-sm me-2"
                v-if="!c.is_blacklisted"
                @click="performAction(c.id, 'blacklist')">
                Blacklist
              </button>

              <button class="btn btn-secondary btn-sm"
                v-if="c.is_blacklisted"
                @click="performAction(c.id, 'unblacklist')">
                Unblacklist
              </button>

            </div>

            <!-- Rejected -->
            <div v-else>
              <span class="text-muted">No actions</span>
            </div>

          </td>
        </tr>
      </tbody>
    </table>

  </div>
</template>