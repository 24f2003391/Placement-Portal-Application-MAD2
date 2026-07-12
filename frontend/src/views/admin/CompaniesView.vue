<script setup>
import { ref, onMounted } from 'vue'
import { useMessageStore } from '@/stores/message'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()

const messageStore = useMessageStore()
const authStore = useAuthStore()
const companies = ref([])
const loading = ref(false)

const search = ref({
  id:'',
  name: '',
  industry: '',
  hr_phone: '',
  website: '',
  approval_status: '',
  is_blacklisted: ''
})

function viewDrives(companyId) {
  router.push({
    name: 'admin-drives',   
    query: { company_id: companyId }
  })
}

async function fetchCompanies() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    Object.entries(search.value).forEach(([key, value]) => {
      if (value !== '' && value !== null) {
        params.append(key, value)
      }
    })
    const res = await fetch(`http://127.0.0.1:5000/api/admin/companies?${params}`,{
      method:"GET",
      headers:{
        "Content-Type": 'application/json',
        Authorization: authStore.getAuthToken(),
      }}
    )
    const data = await res.json()
    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Failed to fetch companies', 'danger')
      return
    }
    const order = { Approved: 1, Applied: 2, Rejected: 3 }
    companies.value = data.sort((a, b) => {
      return order[a.approval_status] - order[b.approval_status]
    })
  } catch (err) {
    messageStore.updateMessages('Something went wrong while fetching companies', 'danger')
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function performAction(id, action) {
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/admin/companies/${id}/${action}`, {
      method: 'PUT',
      headers:{
        "Content-Type": 'application/json',
        Authorization: authStore.getAuthToken(),
      }
    })

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Action failed', 'danger')
      return
    }

    messageStore.updateMessages(data.message, 'success')
    fetchCompanies()

  } catch (err) {
    messageStore.updateMessages('Something went wrong while performing action', 'danger')
    console.error(err)
  }
}

onMounted(fetchCompanies)
</script>

<template>
  <div class="container mt-4">

    <div class="row g-2 mb-3">
      <div class="col">
        <input v-model="search.id" class="form-control" placeholder="ID">
      </div>
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
          <option value="">Blacklist(yes/no)</option>
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

    <div v-if="loading" class="text-center">
      Loading...
    </div>

    <table v-if="!loading" class="table table-bordered table-hover">
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Industry</th>
          <th>Phone</th>
          <th>Website</th>
          <th>Status</th>
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
          <td>
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

            <div v-else-if="c.approval_status === 'Approved'">
              <button class="btn btn-info btn-sm me-2"
                @click="viewDrives(c.id)">
                View Drives
              </button>

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

            <div v-else>
              <span class="text-muted">No actions</span>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

  </div>
</template>