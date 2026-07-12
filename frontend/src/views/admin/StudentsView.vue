<script setup>
import { ref, onMounted } from 'vue'
import { useMessageStore } from '@/stores/message'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()

const messageStore = useMessageStore()
const authStore=useAuthStore()

const students = ref([])
const loading = ref(false)

const programs = ref([]);

function viewApplications(roll_no) {
  router.push({
    name: 'admin-applications',   
    query: { student_id: roll_no }
  })
}

onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:5000/api/programs')
    const data = await res.json()
    programs.value = data
  } catch (err) {
    console.error('Failed to load programs', err)
  }
})

const search = ref({
  name: '',
  roll_no: '',
  phone: '',
  program:'',
  is_blacklisted: ''
})

async function fetchStudents() {
  loading.value = true
  try {
    const params = new URLSearchParams()

    Object.entries(search.value).forEach(([key, value]) => {
      if (value !== '' && value !== null) {
        params.append(key, value)
      }
    })

    const res = await fetch(`http://127.0.0.1:5000/api/admin/students?${params}`,{
      method: 'GET',
      headers:{
        "Content-Type": 'application/json',
        Authorization: authStore.getAuthToken(),
      }})
    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(data.message || 'Failed to fetch students', 'danger')
      return
    }

    students.value = data

  } catch (err) {
    messageStore.updateMessages('Something went wrong while fetching students', 'danger')
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function performAction(roll_no, action) {
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/admin/students/${roll_no}/${action}`, {
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
    fetchStudents()

  } catch (err) {
    messageStore.updateMessages('Something went wrong while performing action', 'danger')
    console.error(err)
  }
}

onMounted(fetchStudents)
</script>

<template>
  <div class="container mt-4">

    <!-- 🔍 Search -->
    <div class="row g-2 mb-3">
      
      <div class="col">
        <input v-model="search.name" class="form-control" placeholder="Name">
      </div>

      <div class="col">
        <input v-model="search.roll_no" class="form-control" placeholder="Roll No">
      </div>

      <div class="col">
        <input v-model="search.phone" class="form-control" placeholder="Phone">
      </div>

      <div class="mb-3">
            <label for="program" class="form-label">Program</label>
            <select 
                id="program"
                class="form-select"
                v-model="search.program">
                <option disabled value="">Select a program</option>
                <option 
                v-for="prog in programs" 
                :key="prog.code" 
                :value="prog.code"
                >
                {{ prog.name }} ({{ prog.code }})
                </option>
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
        <button class="btn btn-primary w-100" @click="fetchStudents">
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
          <th>Roll No</th>
          <th>Name</th>
          <th>Phone</th>
          <th>Program</th>
          <th>CGPA</th>
          <th>Year</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="s in students" :key="s.roll_no">
          <td>{{ s.roll_no }}</td>
          <td>{{ s.name }}</td>
          <td>{{ s.phone_no }}</td>
          <td>{{ s.program_name }}</td>
          <td>{{ s.cgpa }}</td>
          <td>{{ s.year_in_program }}</td>
          <td>
            <button class="btn btn-info btn-sm me-2"
                @click="viewApplications(s.roll_no)">
                View Applications
            </button>

            <button class="btn btn-warning btn-sm me-2"
              v-if="!s.is_blacklisted"
              @click="performAction(s.roll_no, 'blacklist')">
              Blacklist
            </button>

            <button class="btn btn-secondary btn-sm"
              v-if="s.is_blacklisted"
              @click="performAction(s.roll_no, 'unblacklist')">
              Unblacklist
            </button>

          </td>

        </tr>
      </tbody>
    </table>

  </div>
</template>