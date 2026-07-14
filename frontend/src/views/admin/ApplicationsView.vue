<script setup>
import { ref, onMounted } from 'vue'
import { useMessageStore } from '@/stores/message'
import { useAuthStore } from '@/stores/auth'
import DocumentViewer from '@/components/DocumentViewer.vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const authStore = useAuthStore()

const showModal = ref(false)
const loadingResume = ref(false)

const pdfUrl = ref('')
const title = ref('')
const details = ref({})

const messageStore = useMessageStore()

const applications = ref([])
const loading = ref(false)

const search = ref({
  drive_id: '',
  student_roll_no: '',
  status: '',
  start_date: '',
  end_date: ''
})

async function viewResume(application) {
  showModal.value = true
  loadingResume.value = true

  title.value = `Resume - ${application.student_name}`

  details.value = {
    "Application ID": application.id,
    "Student": application.student_name,
    "Roll No": application.student_roll_no,
    "Job": application.job_title,
    "Status": application.status,
    "Applied On": application.application_date
  }

  try {
    const res = await fetch(
      `http://127.0.0.1:5000/api/admin/applications/${application.id}/resume`,
      {
        headers: {
          Authorization: authStore.token,
        }
      }
    )

    if (!res.ok) {
      const data = await res.json()
      messageStore.updateMessages(data.message || 'Failed to load resume','danger')
      closeModal()
      return
    }

    const blob = await res.blob()
    pdfUrl.value = URL.createObjectURL(blob)

  } catch (err) {
    messageStore.updateMessages('Error loading resume','danger')
    closeModal()
    console.error(err)
  } finally {
    loadingResume.value = false
  }
}

function closeModal() {
  URL.revokeObjectURL(pdfUrl.value)
  showModal.value = false
  pdfUrl.value = ''
}

// 🔹 Fetch
async function fetchApplications() {
  loading.value = true
  try {
    const params = new URLSearchParams()

    Object.entries(search.value).forEach(([key, value]) => {
      if (value) params.append(key, value)
    })

    const res = await fetch(`http://127.0.0.1:5000/api/admin/applications?${params}`,
      {
        headers: {
          Authorization: authStore.token,
        }
      }
    )
    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Failed to fetch applications','danger')
      return
    }

    applications.value = data

  } catch (err) {
    messageStore.updateMessages('Error fetching applications','danger')
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {

    if (route.query.student_id) {
        search.value.student_roll_no = route.query.student_id
    }

    if (route.query.drive_id) {
        search.value.drive_id = route.query.drive_id
    }

    fetchApplications()
})
</script>

<template>
  <div class="container mt-4">

    <h2 class="mb-3">Applications</h2>

    <!-- 🔍 Search -->
    <div class="row g-2 mb-3">

      <div class="col">
        <input v-model="search.drive_id" class="form-control" placeholder="Drive ID">
      </div>

      <div class="col">
        <input v-model="search.student_id" class="form-control" placeholder="Student Roll No">
      </div>

      <div class="col">
        <input type="date" v-model="search.start_date" class="form-control">
      </div>

      <div class="col">
        <input type="date" v-model="search.end_date" class="form-control">
      </div>

      <div class="col">
        <select v-model="search.status" class="form-select">
          <option value="">All Status</option>
          <option>Applied</option>
          <option>Shortlisted</option>
          <option>Selected</option>
          <option>Rejected</option>
          <option>Cancelled</option>
        </select>
      </div>

      <div class="col">
        <button class="btn btn-primary w-100" @click="fetchApplications">
          Search
        </button>
      </div>

    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center">
      Loading...
    </div>

    <!-- Table -->
    <table v-if="!loading" class="table table-bordered table-hover">
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>Drive ID</th>
          <th>Job Title</th>
          <th>Student Roll</th>
          <th>Student Name</th>
          <th>Application Date</th>
          <th>Status</th>
          <th>Details</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="a in applications" :key="a.id">
          <td>{{ a.id }}</td>
          <td>{{ a.drive_id }}</td>
          <td>{{ a.job_title }}</td>
          <td>{{ a.student_roll_no }}</td>
          <td>{{ a.student_name }}</td>
          <td>{{ a.application_date }}</td>

          <td>
            <span :class="{
              'badge bg-warning text-dark': a.status === 'Applied',
              'badge bg-info': a.status === 'Shortlisted',
              'badge bg-success': a.status === 'Selected',
              'badge bg-danger': a.status === 'Rejected',
              'badge bg-secondary': a.status === 'Cancelled'
            }">
              {{ a.status }}
            </span>
          </td>

          <!-- View Details -->
          <td>
            <button class="btn btn-info btn-sm"
                :disabled="loadingResume"
                @click="viewResume(a)">
                View
            </button>
          </td>

        </tr>
      </tbody>
    </table>
    <DocumentViewer 
      :show="showModal"
      :title="title"
      :pdfUrl="pdfUrl"
      :details="details"
      @close="closeModal">
    </DocumentViewer>
  </div>
</template>