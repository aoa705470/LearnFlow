import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import HomeView from './HomeView.vue'

describe('HomeView', () => {
  it('shows the application identity without demo learning data', () => {
    const wrapper = mount(HomeView)

    expect(wrapper.get('h1').text()).toBe('LearnFlow')
    expect(wrapper.text()).toContain('个人学习工作台')
  })
})
