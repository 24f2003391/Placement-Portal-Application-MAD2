<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const router = useRouter()

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)
const submitting = ref(false)

const profile = ref({
  name: '',
  email: '',
  phone_no: '',
  program: '',
  cgpa: '',
  year_in_program: '',
  password: '',
  confirm_password: ''
})

async function fetchProfile() {
  loading.value = true

  try {

    const res = await fetch(
      'http://127.0.0.1:5000/api/student/profile',
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: authStore.token
        }
      }
    )

    const data = await res.json()

    if (!res.ok) {
      messageStore.updateMessages(
        data.message || 'Failed to load profile.',
        'danger'
      )
      return
    }

    profile.value.name = data.name
    profile.value.email = data.email
    profile.value.phone_no = data.phone_no
    profile.value.program = data.program
    profile.value.cgpa = data.cgpa
    profile.value.year_in_program = data.year_in_program

  } catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Unable to connect to server.',
      'danger'
    )

  } finally {

    loading.value = false

  }
}

async function saveProfile() {

  if (
    profile.value.password &&
    profile.value.password !== profile.value.confirm_password
  ) {

    messageStore.updateMessages(
      'Passwords do not match.',
      'danger'
    )

    return
  }

  submitting.value = true

  try {

    const payload = {
      name: profile.value.name,
      email: profile.value.email,
      phone_no: profile.value.phone_no,
      cgpa: profile.value.cgpa,
      year_in_program: profile.value.year_in_program,
      password: profile.value.password
    }

    const res = await fetch(
      'http://127.0.0.1:5000/api/student/profile',
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: authStore.token
        },
        body: JSON.stringify(payload)
      }
    )

    const data = await res.json()

    if (!res.ok) {

      messageStore.updateMessages(
        data.message || 'Failed to update profile.',
        'danger'
      )

      return
    }

    messageStore.updateMessages(
      data.message,
      'success'
    )

    profile.value.password = ''
    profile.value.confirm_password = ''

    router.push('/student')

  } catch (err) {

    console.error(err)

    messageStore.updateMessages(
      'Unable to connect to server.',
      'danger'
    )

  } finally {

    submitting.value = false

  }

}

onMounted(fetchProfile)
</script>

<template>

<div class="container mt-4">

  <div class="row justify-content-center">

    <div class="col-lg-8">

      <div class="card shadow-sm">

        <div class="card-header">

          <h4 class="mb-0">

            Edit Profile

          </h4>

        </div>

        <div
          v-if="loading"
          class="card-body text-center">

          <div class="spinner-border"></div>

        </div>

        <div
          v-else
          class="card-body">

          <form @submit.prevent="saveProfile">

            <div class="mb-3">

              <label class="form-label">

                Name

              </label>

              <input
                v-model="profile.name"
                type="text"
                class="form-control"
                required>

            </div>

            <div class="mb-3">

              <label class="form-label">

                Email

              </label>

              <input
                v-model="profile.email"
                type="email"
                class="form-control"
                required>

            </div>

            <div class="mb-3">

              <label class="form-label">

                Phone Number

              </label>

              <input
                v-model="profile.phone_no"
                type="text"
                class="form-control"
                required>

            </div>

            <div class="mb-3">

              <label class="form-label">

                Program

              </label>

              <input
                v-model="profile.program"
                type="text"
                class="form-control"
                disabled>

            </div>

            <div class="row">

              <div class="col-md-6 mb-3">

                <label class="form-label">

                  CGPA

                </label>

                <input
                  v-model="profile.cgpa"
                  type="number"
                  step="0.01"
                  min="0"
                  max="10"
                  class="form-control"
                  required>

              </div>

              <div class="col-md-6 mb-3">

                <label class="form-label">

                  Year In Program

                </label>

                <input
                  v-model="profile.year_in_program"
                  type="number"
                  min="1"
                  class="form-control"
                  required>

              </div>

            </div>

            <hr>

            <h6>

              Change Password

            </h6>

            <p class="text-muted">

              Leave these fields blank if you do not wish to change your password.

            </p>

            <div class="mb-3">

              <label class="form-label">

                New Password

              </label>

              <input
                v-model="profile.password"
                type="password"
                class="form-control">

            </div>

            <div class="mb-4">

              <label class="form-label">

                Confirm Password

              </label>

              <input
                v-model="profile.confirm_password"
                type="password"
                class="form-control">

            </div>

            <div class="d-flex justify-content-end">

              <button
                type="button"
                class="btn btn-secondary me-2"
                @click="router.push('/student')">

                Cancel

              </button>

              <button
                type="submit"
                class="btn btn-primary"
                :disabled="submitting">

                {{ submitting ? 'Saving...' : 'Save Changes' }}

              </button>

            </div>

          </form>

        </div>

      </div>

    </div>

  </div>

</div>

</template>