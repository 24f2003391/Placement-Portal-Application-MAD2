<script setup>
import { ref, watch } from 'vue'

import { useAuthStore } from '@/stores/auth'
import { useMessageStore } from '@/stores/message'

const props = defineProps({
  show: Boolean,
  application: Object
})

const emit = defineEmits([
  'close',
  'scheduled'
])

const authStore = useAuthStore()
const messageStore = useMessageStore()

const loading = ref(false)

const form = ref({
  interview_date: '',
  interview_time: '',
  interview_details: ''
})

watch(
  () => props.application,
  (application) => {

    if (!application) return

    if (application.interview) {

      const dt = new Date(application.interview.datetime)

      form.value.interview_date =
        dt.toISOString().split('T')[0]

      form.value.interview_time =
        dt.toTimeString().slice(0,5)

      form.value.interview_details =
        application.interview.details

    }
    else {

      form.value = {
        interview_date:'',
        interview_time:'',
        interview_details:''
      }

    }

  },
  {
    immediate:true
  }
)

async function scheduleInterview(){

  if(
    !form.value.interview_date ||
    !form.value.interview_time ||
    !form.value.interview_details
  ){
    messageStore.updateMessages(
      'All fields are required.',
      'warning'
    )
    return
  }

  loading.value=true

  try{

    const interview_datetime =
      `${form.value.interview_date} ${form.value.interview_time}`

    const res = await fetch(

      `http://127.0.0.1:5000/api/company/applications/${props.application.application_id}/interview`,

      {

        method:'POST',

        headers:{
          Authorization: authStore.token,
          'Content-Type':'application/json'
        },

        body:JSON.stringify({

          interview_datetime,

          interview_details:form.value.interview_details

        })

      }

    )

    const data = await res.json()

    if(!res.ok){

      messageStore.updateMessages(
        data.message,
        'danger'
      )

      return

    }

    messageStore.updateMessages(
      data.message
    )

    emit('scheduled')

  }

  catch(err){

    console.error(err)

    messageStore.updateMessages(
      'Unable to schedule interview.',
      'danger'
    )

  }

  finally{

    loading.value=false

  }

}

function close(){

  emit('close')

}
</script>

<template>

<div
v-if="show"
class="modal fade show d-block">

<div
class="modal-dialog">

<div
class="modal-content">

<div
class="modal-header">

<h5
class="modal-title">

{{ application?.interview ? 'Reschedule Interview' : 'Schedule Interview' }}

</h5>

<button
class="btn-close"
@click="close">
</button>

</div>

<div
class="modal-body">

<div class="mb-3">

<label class="form-label">

Student

</label>

<input
class="form-control"
:disabled="true"
:value="application?.student_name">

</div>

<div class="mb-3">

<label class="form-label">

Roll Number

</label>

<input
class="form-control"
:disabled="true"
:value="application?.roll_no">

</div>

<div class="row">

<div class="col-md-6 mb-3">

<label class="form-label">

Interview Date

</label>

<input
type="date"
class="form-control"
v-model="form.interview_date">

</div>

<div class="col-md-6 mb-3">

<label class="form-label">

Interview Time

</label>

<input
type="time"
class="form-control"
v-model="form.interview_time">

</div>

</div>

<div class="mb-3">

<label class="form-label">

Interview Details

</label>

<textarea
rows="5"
class="form-control"
v-model="form.interview_details">
</textarea>

</div>

</div>

<div
class="modal-footer">

<button
class="btn btn-secondary"
@click="close">

Close

</button>

<button
class="btn btn-primary"
@click="scheduleInterview"
:disabled="loading">

{{ loading
? 'Saving...'
: (application?.interview
? 'Reschedule'
: 'Schedule')
}}

</button>

</div>

</div>

</div>

</div>

<div
v-if="show"
class="modal-backdrop fade show">
</div>

</template>