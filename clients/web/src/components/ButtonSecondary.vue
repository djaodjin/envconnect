<template>
  <v-btn
    v-on="$listeners"
    v-bind="$attrs"
    :to="to"
    :block="!display || display !== 'inline'"
    :type="!type ? 'button' : type"
    :color="!color ? 'secondary' : color"
    large
    outlined
  >
    <slot></slot>
  </v-btn>
</template>

<script>
export default {
  name: 'ButtonSecondary',
  props: ['color', 'to', 'display', 'type'],
}
</script>
