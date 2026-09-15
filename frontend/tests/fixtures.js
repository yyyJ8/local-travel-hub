/**
 * 渲染级自测夹具：字段结构与后端 models/schemas.py 保持一致
 */
export const shopFixture = {
  id: 'S001',
  name: '蜀大侠火锅（春熙路店）',
  category: '美食',
  subCategory: '火锅',
  rating: 4.8,
  reviewCount: 8642,
  avgPrice: 128,
  tags: ['麻辣牛肉', '毛肚'],
  district: '锦江区',
  address: '成都市锦江区春熙路东段 18 号 3 层',
  coverColor: '#ff6633',
  coverTag: '火锅',
  packageCount: 4
}

export const hotelFixture = {
  id: 'H001',
  name: '成都太古里博舍酒店',
  city: '成都',
  star: 5,
  rating: 4.9,
  reviewCount: 6420,
  minPrice: 1280,
  district: '锦江区',
  address: '成都市锦江区笔帖式街 81 号',
  facilities: ['免费WiFi', '室内泳池', '健身房'],
  tags: ['太古里核心'],
  coverColor: '#0050b3',
  coverTag: '豪华五星',
  roomCount: 4
}

export const homeFixture = {
  banners: [
    { id: 'B001', title: '春日美食节', subtitle: '精选火锅 · 5 折起', colorFrom: '#ff7a45', colorTo: '#ff4d4f', targetType: 'shop', targetId: 'S001' }
  ],
  categories: [
    { id: 'C001', name: '美食', icon: 'Food', color: '#ff6633', targetType: 'shop', targetCategory: '美食' },
    { id: 'C002', name: '休闲娱乐', icon: 'Coffee', color: '#722ed1', targetType: 'shop', targetCategory: '休闲娱乐' },
    { id: 'C003', name: '酒店', icon: 'OfficeBuilding', color: '#0086f6', targetType: 'hotel', targetCategory: '' }
  ],
  shops: [shopFixture],
  hotels: [hotelFixture]
}

export const shopDetailFixture = {
  ...shopFixture,
  businessHours: '11:00 - 次日 02:00',
  phone: '028-8611-0001',
  packages: [
    { id: 'S001-P01', name: '双人套餐·麻辣牛肉', price: 236, originalPrice: 298, sold: 3709, desc: '双人套餐，含麻辣牛肉等招牌菜。' },
    { id: 'S001-P02', name: '四人套餐·毛肚', price: 435, originalPrice: 520, sold: 1200, desc: '四人套餐，含毛肚等招牌菜。' }
  ],
  comments: [
    { id: 'S001-C01', user: '阿宝', avatarColor: '#ff7875', rating: 5, content: '麻辣牛肉真的很惊艳，分量足，服务也热情！', date: '2026-08-01' }
  ]
}

export const hotelDetailFixture = {
  ...hotelFixture,
  intro: '位于太古里核心区，庭院式布局兼顾私密与静谧。',
  rooms: [
    { id: 'H001-R01', name: '高级大床房', area: 28, bedType: '1.8m 大床', breakfast: '含单早', window: '有窗', cancelPolicy: '免费取消', price: 1280, originalPrice: 1600, remain: 3 }
  ],
  reviews: [
    { id: 'H001-V01', user: '小鹿乱撞', avatarColor: '#69c0ff', rating: 5, content: '位置非常方便，离地铁口很近。', date: '2026-08-02', roomType: '高级大床房' }
  ]
}

export const ordersFixture = {
  total: 3,
  items: [
    {
      orderNo: 'ORD202609091001', type: 'shop', targetId: 'S001', targetName: '蜀大侠火锅（春熙路店）',
      itemId: 'S001-P02', itemName: '双人套餐·麻辣牛肉', name: '张三', phone: '13800001111',
      bookTime: '2026-09-20', checkOut: '', nights: 0, count: 1, amount: 474,
      status: '待使用', createdAt: '2026-09-09 10:00:00', coverColor: '#ff6633', coverTag: '火锅'
    },
    {
      orderNo: 'ORD202609111002', type: 'hotel', targetId: 'H001', targetName: '成都太古里博舍酒店',
      itemId: 'H001-R01', itemName: '高级大床房', name: '张三', phone: '13800001111',
      bookTime: '2026-09-25', checkOut: '2026-09-27', nights: 2, count: 1, amount: 2560,
      status: '待使用', createdAt: '2026-09-11 10:00:00', coverColor: '#0050b3', coverTag: '豪华五星'
    },
    {
      orderNo: 'ORD202608311003', type: 'shop', targetId: 'S009', targetName: '足下生辉足疗SPA（桐梓林店）',
      itemId: 'S009-P01', itemName: '单人套餐·精油全身按摩', name: '李四', phone: '13900002222',
      bookTime: '2026-09-01', checkOut: '', nights: 0, count: 1, amount: 188,
      status: '已取消', createdAt: '2026-08-31 10:00:00', coverColor: '#722ed1', coverTag: 'SPA'
    }
  ]
}
