<script setup>
import { ref,onMounted,computed } from 'vue';
import { useRouter } from 'vue-router';
import { useMessageStore } from '@/stores/message';

const router=useRouter();
const messageStore = useMessageStore()

const email = ref('');
const password = ref('');
const name = ref('');
const roll_no = ref('');
const phone_no = ref('');
const program_code = ref(null);
const cgpa = ref('');
const year_in_program = ref('');

const passerror = ref('');
const emailStatus = ref('');
const rollStatus = ref('');
const phoneStatus = ref('');
const formError = ref('');

const programs = ref([]);

const selectedProgram = computed(() =>
    programs.value.find(p => p.code === program_code.value)
)

onMounted(async () => {
  try {
    const res = await fetch('http://127.0.0.1:5000/api/programs')
    const data = await res.json()
    programs.value = data
  } catch (err) {
    console.error('Failed to load programs', err)
  }
})

const validatePassword = () => {
  if (password.value.length < 8) {
    passerror.value = 'Password must be at least 8 characters'
    return false
  } else {
    passerror.value = ''
    return true
  }
}

const checkEmail = async () => {
  emailStatus.value = ''
  if (!email.value) return
  try {
    const response = await fetch('http://127.0.0.1:5000/api/check-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value })
    })
    const data = await response.json()
    if (!response.ok) {
      messageStore.updateMessages(`Email check failed: ${data.message}`,'danger')
      return
    } else {
      emailStatus.value = data.available
        ? '✅ Email available'
        : '❌ Email already registered'
    }
  } catch (error) {
    alert('Something went wrong while checking email')
    console.error(error)
  }
}

const checkPhone = async () => {
  phoneStatus.value = ''
  if (!phone_no.value) return

  try {
    const response = await fetch('http://127.0.0.1:5000/api/check-phone', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone_no: phone_no.value })
    })

    const data = await response.json()

    if (!response.ok) {
      messageStore.updateMessages(`Phone check failed: ${data.message || 'Unknown error'}`,'danger')
      return
    } else {
      phoneStatus.value = data.available
        ? '✅ Phone available'
        : '❌ Phone already registered'
    }

  } catch (error) {
    alert('Something went wrong while checking phone number')
    console.error(error)
  }
}

const checkRoll = async () => {
  rollStatus.value = ''
  if (!roll_no.value) return

  try {
    const response = await fetch('http://127.0.0.1:5000/api/check-roll', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ roll_no: roll_no.value })
    })

    const data = await response.json()

    if (!response.ok) {
      messageStore.updateMessages(`Roll number check failed: ${data.message}`,'danger')
      return
    } else {
      rollStatus.value = data.available
        ? '✅ Roll number available'
        : '❌ Roll number already registered'
    }

  } catch (error) {
    alert('Something went wrong while checking roll number')
    console.error(error)
  }
}
async function register() {
  formError.value = ''
  if (!validatePassword()) {
    alert('Invalid password')
    return
  }
  if (!email.value || !password.value || !name.value || !roll_no.value || !phone_no.value || !program_code.value || !cgpa.value || !year_in_program.value) {
    messageStore.updateMessages(
    'All fields are required',
    'danger'
)
    return
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/api/student/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        name: name.value,
        roll_no: roll_no.value,
        phone_no: phone_no.value,
        program_code: program_code.value,
        cgpa: cgpa.value,
        year_in_program: year_in_program.value
      })
    })

    const data = await response.json()

    if (!response.ok) {
      formError.value = data.message
      return
    }
    messageStore.updateMessages(`${data.message}`)
    router.push({name:'login'})

  } catch (err) {
    formError.value = 'Something went wrong'
    console.error(err)
  }
}
</script>

<template>
  <div class="container-fluid d-flex justify-content-center align-items-center  pt-5 bg-light">
    <div class="card shadow p-4" style="width: 420px;">
      <h3 class="text-center mb-4">Student Register</h3>

      <form @submit.prevent="register">

        <div class="mb-3">
          <label for="name" class="form-label">Full Name</label>
          <input 
            id="name"
            type="text"
            class="form-control" 
            v-model="name" 
            placeholder="Enter full name"
          >
        </div>

        <div class="mb-3">
          <label for="roll" class="form-label">Roll Number</label>
          <input 
            id="roll"
            type="text"
            class="form-control" 
            v-model="roll_no" 
            placeholder="Enter roll number"
            @blur="checkRoll"
          >
          <div class="form-text">{{ rollStatus }}</div>
        </div>

        <div class="mb-3">
          <label for="phone" class="form-label">Phone Number</label>
          <input 
            id="phone"
            type="text"
            class="form-control" 
            v-model="phone_no" 
            placeholder="Enter phone number"
            @blur="checkPhone"
          >
          <div class="form-text">{{ phoneStatus }}</div>
        </div>

        <div class="mb-3">
            <label for="program" class="form-label">Program</label>
            <select 
                id="program"
                class="form-select"
                v-model="program_code">
                <option disabled value="">Select a program</option>
                <option 
                v-for="prog in programs" 
                v-bind:key="prog.code" 
                v-bind:value="prog.code"
                >
                {{ prog.name }} ({{ prog.code }})
                </option>
            </select>
        </div> 

        <div class="mb-3">
          <label for="cgpa" class="form-label">CGPA</label>
          <input 
            id="cgpa"
            type="text"
            class="form-control" 
            v-model="cgpa" 
            placeholder="Enter CGPA (0–10)"
          >
        </div>

        <div class="mb-3">
          <label for="year" class="form-label">Year in Program</label>
          <input 
            id="year"
            type="number"
            class="form-control"
            v-model="year_in_program"
            placeholder="Enter current year"
            min="1"
            :max="prog?.duration"
            />
            <div class="form-text" v-if="selectedProgram">
                Program duration: {{ selectedProgram.duration }} years
            </div>
        </div>

        <div class="mb-3">
          <label for="email" class="form-label">Email Address</label>
          <input 
            id="email"
            type="email"
            class="form-control" 
            v-model="email" 
            placeholder="Enter email"
            @blur="checkEmail"
          >
          <div class="form-text">{{ emailStatus }}</div>
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input 
            id="password"
            type="password"
            class="form-control"
            v-model="password"
            @input="validatePassword"
            placeholder="Enter password"
          >
          <div class="form-text text-danger">{{ passerror }}</div>
        </div>

        <div class="text-danger mb-2">{{ formError }}</div>

        <button class="btn btn-primary w-100">Register</button>

      </form>
    </div>
  </div>
</template>